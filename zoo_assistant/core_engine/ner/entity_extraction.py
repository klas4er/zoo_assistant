import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    Doc
)
import pymorphy2
from yargy import Parser
from yargy.tokenizer import MorphTokenizer
from yargy.predicates import gram, dictionary, type as type_predicate
from yargy.pipelines import morph_pipeline
from yargy.rule import Rule
from yargy import rule

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Entity(BaseModel):
    text: str
    type: str
    start: int
    end: int
    value: Optional[Any] = None
    normalized: Optional[str] = None

class EntityExtractor:
    def __init__(self):
        """Initialize the entity extractor with Natasha components."""
        logger.info("Initializing NER components")
        
        # Initialize Natasha components
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        
        # Initialize embeddings and taggers
        self.emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.emb)
        self.syntax_parser = NewsSyntaxParser(self.emb)
        self.ner_tagger = NewsNERTagger(self.emb)
        
        # Initialize PyMorphy2 for morphological analysis
        self.morph = pymorphy2.MorphAnalyzer()
        
        # Initialize Yargy tokenizer
        self.tokenizer = MorphTokenizer()
        
        # Initialize custom rules
        self._init_custom_rules()
        
        logger.info("NER components initialized successfully")
    
    def _init_custom_rules(self):
        """Initialize custom extraction rules for zoo-specific entities."""
        # Animal species dictionary
        self.animal_species = [
            'тигр', 'тигрица', 'лев', 'львица', 'слон', 'жираф', 'зебра', 'обезьяна',
            'горилла', 'шимпанзе', 'медведь', 'волк', 'лиса', 'енот', 'панда', 'коала',
            'кенгуру', 'крокодил', 'аллигатор', 'змея', 'питон', 'удав', 'черепаха',
            'игуана', 'ящерица', 'попугай', 'пингвин', 'фламинго', 'журавль', 'павлин',
            'бегемот', 'носорог', 'зебра', 'антилопа', 'жираф', 'верблюд', 'лама'
        ]
        
        # Behavior dictionary
        self.behaviors = [
            'спит', 'ест', 'играет', 'отдыхает', 'плавает', 'бегает', 'прыгает',
            'охотится', 'дерется', 'кормит', 'чистит', 'вылизывает', 'купается',
            'греется', 'прячется', 'наблюдает', 'кричит', 'рычит', 'воет',
            'агрессивный', 'спокойный', 'активный', 'вялый', 'игривый'
        ]
        
        # Health status dictionary
        self.health_statuses = [
            'здоров', 'болен', 'ранен', 'выздоравливает', 'слабый', 'сильный',
            'нормальный', 'стабильный', 'критический', 'беременная', 'кормящая'
        ]
        
        # Food dictionary
        self.foods = [
            'мясо', 'рыба', 'фрукты', 'овощи', 'трава', 'листья', 'сено',
            'зерно', 'орехи', 'насекомые', 'грызуны', 'кролик', 'курица'
        ]
        
        # Create Yargy rules
        
        # Weight rule (e.g., "42 килограмма", "2.5 кг")
        WEIGHT_WORDS = morph_pipeline(['килограмм', 'кг', 'грамм', 'г'])
        INT = type_predicate('INT')
        FLOAT = type_predicate('FLOAT')
        NUMBER = INT | FLOAT
        
        self.weight_rule = rule(
            NUMBER,
            WEIGHT_WORDS
        )
        self.weight_parser = Parser(self.weight_rule)
        
        # Length/height rule (e.g., "4 метра 30 сантиметров", "1.65 м")
        LENGTH_WORDS = morph_pipeline(['метр', 'м', 'сантиметр', 'см'])
        
        self.length_rule = rule(
            NUMBER,
            LENGTH_WORDS
        )
        self.length_parser = Parser(self.length_rule)
        
        # Temperature rule (e.g., "28 градусов")
        TEMP_WORDS = morph_pipeline(['градус', '°C', '°'])
        
        self.temp_rule = rule(
            NUMBER,
            TEMP_WORDS
        )
        self.temp_parser = Parser(self.temp_rule)
        
        # Animal species rule
        ANIMAL_WORDS = morph_pipeline(self.animal_species)
        self.animal_parser = Parser(ANIMAL_WORDS)
        
        # Behavior rule
        BEHAVIOR_WORDS = morph_pipeline(self.behaviors)
        self.behavior_parser = Parser(BEHAVIOR_WORDS)
        
        # Health status rule
        HEALTH_WORDS = morph_pipeline(self.health_statuses)
        self.health_parser = Parser(HEALTH_WORDS)
        
        # Food rule
        FOOD_WORDS = morph_pipeline(self.foods)
        self.food_parser = Parser(FOOD_WORDS)
    
    def _extract_numeric_value(self, match_text: str) -> float:
        """Extract numeric value from a matched text."""
        # Extract all numbers from the text
        numbers = re.findall(r'\d+[.,]?\d*', match_text)
        if numbers:
            # Convert to float, handling both comma and dot as decimal separator
            return float(numbers[0].replace(',', '.'))
        return None
    
    def _extract_with_parser(self, text: str, parser: Parser, entity_type: str) -> List[Entity]:
        """Extract entities using a Yargy parser."""
        entities = []
        for match in parser.findall(text):
            start, end = match.span
            match_text = text[start:end]
            
            # For numeric entities, extract the value
            value = None
            if entity_type in ['weight', 'length', 'temperature']:
                value = self._extract_numeric_value(match_text)
            
            entities.append(Entity(
                text=match_text,
                type=entity_type,
                start=start,
                end=end,
                value=value
            ))
        
        return entities
    
    def _extract_custom_entities(self, text: str) -> List[Entity]:
        """Extract custom entities using Yargy rules."""
        entities = []
        
        # Extract weights
        weight_entities = self._extract_with_parser(text, self.weight_parser, 'weight')
        entities.extend(weight_entities)
        
        # Extract lengths
        length_entities = self._extract_with_parser(text, self.length_parser, 'length')
        entities.extend(length_entities)
        
        # Extract temperatures
        temp_entities = self._extract_with_parser(text, self.temp_parser, 'temperature')
        entities.extend(temp_entities)
        
        # Extract animal species
        animal_entities = self._extract_with_parser(text, self.animal_parser, 'animal_species')
        entities.extend(animal_entities)
        
        # Extract behaviors
        behavior_entities = self._extract_with_parser(text, self.behavior_parser, 'behavior')
        entities.extend(behavior_entities)
        
        # Extract health statuses
        health_entities = self._extract_with_parser(text, self.health_parser, 'health_status')
        entities.extend(health_entities)
        
        # Extract foods
        food_entities = self._extract_with_parser(text, self.food_parser, 'food')
        entities.extend(food_entities)
        
        return entities
    
    def _extract_natasha_entities(self, text: str) -> List[Entity]:
        """Extract entities using Natasha NER."""
        # Process the text with Natasha
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)
        doc.parse_syntax(self.syntax_parser)
        doc.tag_ner(self.ner_tagger)
        
        # Convert spans to our Entity format
        entities = []
        for span in doc.spans:
            # Map Natasha entity types to our types
            entity_type = span.type
            if entity_type == 'PER':
                entity_type = 'person'
            elif entity_type == 'LOC':
                entity_type = 'location'
            elif entity_type == 'ORG':
                entity_type = 'organization'
            
            entities.append(Entity(
                text=span.text,
                type=entity_type,
                start=span.start,
                end=span.stop,
                normalized=span.normal
            ))
        
        return entities
    
    def _extract_regex_entities(self, text: str) -> List[Entity]:
        """Extract entities using regex patterns."""
        entities = []
        
        # Date pattern (e.g., "01.01.2023", "1 января 2023")
        date_pattern = r'\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b|\b\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+\d{4}\b'
        for match in re.finditer(date_pattern, text):
            entities.append(Entity(
                text=match.group(),
                type='date',
                start=match.start(),
                end=match.end()
            ))
        
        # Time pattern (e.g., "14:30", "2:45")
        time_pattern = r'\b\d{1,2}[:]\d{2}\b'
        for match in re.finditer(time_pattern, text):
            entities.append(Entity(
                text=match.group(),
                type='time',
                start=match.start(),
                end=match.end()
            ))
        
        # Percentage pattern (e.g., "50%", "70 процентов")
        percentage_pattern = r'\b\d+(?:[.,]\d+)?%|\b\d+(?:[.,]\d+)?\s+процент(?:а|ов)?\b'
        for match in re.finditer(percentage_pattern, text):
            value = self._extract_numeric_value(match.group())
            entities.append(Entity(
                text=match.group(),
                type='percentage',
                start=match.start(),
                end=match.end(),
                value=value
            ))
        
        # Age pattern (e.g., "5 лет", "2 года")
        age_pattern = r'\b\d+\s+(?:лет|год(?:а)?)\b'
        for match in re.finditer(age_pattern, text):
            value = self._extract_numeric_value(match.group())
            entities.append(Entity(
                text=match.group(),
                type='age',
                start=match.start(),
                end=match.end(),
                value=value
            ))
        
        return entities
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract all entities from the text."""
        # Combine entities from all extraction methods
        entities = []
        
        # Extract using Natasha NER
        natasha_entities = self._extract_natasha_entities(text)
        entities.extend(natasha_entities)
        
        # Extract using custom rules
        custom_entities = self._extract_custom_entities(text)
        entities.extend(custom_entities)
        
        # Extract using regex patterns
        regex_entities = self._extract_regex_entities(text)
        entities.extend(regex_entities)
        
        # Sort entities by start position
        entities.sort(key=lambda e: e.start)
        
        return entities
    
    def extract_animal_info(self, text: str) -> Dict[str, Any]:
        """Extract structured animal information from text."""
        entities = self.extract_entities(text)
        
        # Initialize result dictionary
        result = {
            'name': None,
            'species': None,
            'measurements': {
                'weight': None,
                'length': None,
                'temperature': None,
                'age': None
            },
            'behavior': None,
            'health_status': None,
            'feeding': {
                'food_type': None,
                'quantity': None
            },
            'environment': {
                'temperature': None,
                'humidity': None
            },
            'entities': [e.dict() for e in entities]
        }
        
        # Extract animal name and species
        for entity in entities:
            if entity.type == 'person':
                # Assume the first person entity might be the animal name
                if result['name'] is None:
                    result['name'] = entity.text
            
            elif entity.type == 'animal_species':
                if result['species'] is None:
                    result['species'] = entity.text
            
            # Extract measurements
            elif entity.type == 'weight':
                if result['measurements']['weight'] is None:
                    result['measurements']['weight'] = entity.value
            
            elif entity.type == 'length':
                if result['measurements']['length'] is None:
                    result['measurements']['length'] = entity.value
            
            elif entity.type == 'temperature':
                # Determine if it's body temperature or environmental
                # This is a simplification - in reality would need context analysis
                if 'тела' in text[max(0, entity.start-10):entity.end+10]:
                    result['measurements']['temperature'] = entity.value
                else:
                    result['environment']['temperature'] = entity.value
            
            elif entity.type == 'age':
                if result['measurements']['age'] is None:
                    result['measurements']['age'] = entity.value
            
            # Extract behavior and health
            elif entity.type == 'behavior':
                if result['behavior'] is None:
                    result['behavior'] = entity.text
            
            elif entity.type == 'health_status':
                if result['health_status'] is None:
                    result['health_status'] = entity.text
            
            # Extract feeding info
            elif entity.type == 'food':
                if result['feeding']['food_type'] is None:
                    result['feeding']['food_type'] = entity.text
        
        # Try to find feeding quantity by looking for weight entities near food entities
        food_entity = next((e for e in entities if e.type == 'food'), None)
        if food_entity:
            # Look for weight entities within 20 characters of the food entity
            for entity in entities:
                if entity.type == 'weight' and abs(entity.start - food_entity.start) < 20:
                    result['feeding']['quantity'] = entity.value
                    break
        
        return result

# Singleton instance
_extractor = None

def get_extractor():
    """Get or create a singleton instance of the entity extractor."""
    global _extractor
    if _extractor is None:
        _extractor = EntityExtractor()
    return _extractor