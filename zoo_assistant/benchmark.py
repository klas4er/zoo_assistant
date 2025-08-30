#!/usr/bin/env python3
"""
Benchmark script for Zoo Assistant
"""
import os
import sys
import time
import argparse
import logging
import statistics
from pprint import pprint
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def benchmark_asr(audio_files, num_runs=3):
    """Benchmark the ASR (Automatic Speech Recognition) component."""
    logger.info(f"Benchmarking ASR with {len(audio_files)} audio files, {num_runs} runs each")
    
    try:
        from core_engine.asr.speech_recognition import get_recognizer
        
        # Get the recognizer
        recognizer = get_recognizer()
        
        results = {}
        
        for audio_file in audio_files:
            logger.info(f"Testing file: {audio_file}")
            file_results = []
            
            for run in range(num_runs):
                logger.info(f"Run {run + 1}/{num_runs}")
                
                # Process the audio file
                start_time = time.time()
                result = recognizer.process_audio(audio_file)
                end_time = time.time()
                
                # Calculate metrics
                processing_time = end_time - start_time
                audio_duration = result.audio_duration
                rtf = processing_time / audio_duration
                
                file_results.append({
                    'processing_time': processing_time,
                    'audio_duration': audio_duration,
                    'rtf': rtf
                })
                
                logger.info(f"Processing time: {processing_time:.2f}s")
                logger.info(f"Audio duration: {audio_duration:.2f}s")
                logger.info(f"Real-time factor: {rtf:.2f}x")
            
            # Calculate average metrics
            avg_processing_time = statistics.mean([r['processing_time'] for r in file_results])
            avg_rtf = statistics.mean([r['rtf'] for r in file_results])
            
            results[os.path.basename(audio_file)] = {
                'runs': file_results,
                'avg_processing_time': avg_processing_time,
                'avg_rtf': avg_rtf,
                'audio_duration': file_results[0]['audio_duration']
            }
            
            logger.info(f"Average processing time: {avg_processing_time:.2f}s")
            logger.info(f"Average real-time factor: {avg_rtf:.2f}x")
        
        return results
    
    except Exception as e:
        logger.error(f"Error benchmarking ASR: {str(e)}")
        return None

def benchmark_ner(texts, num_runs=3):
    """Benchmark the NER (Named Entity Recognition) component."""
    logger.info(f"Benchmarking NER with {len(texts)} texts, {num_runs} runs each")
    
    try:
        from core_engine.ner.entity_extraction import get_extractor
        
        # Get the extractor
        extractor = get_extractor()
        
        results = {}
        
        for i, text in enumerate(texts):
            logger.info(f"Testing text {i + 1}/{len(texts)}")
            text_results = []
            
            for run in range(num_runs):
                logger.info(f"Run {run + 1}/{num_runs}")
                
                # Extract entities
                start_time = time.time()
                entities = extractor.extract_entities(text)
                entity_time = time.time() - start_time
                
                # Extract structured data
                start_time = time.time()
                structured_data = extractor.extract_animal_info(text)
                structured_time = time.time() - start_time
                
                total_time = entity_time + structured_time
                
                text_results.append({
                    'entity_time': entity_time,
                    'structured_time': structured_time,
                    'total_time': total_time,
                    'num_entities': len(entities)
                })
                
                logger.info(f"Entity extraction time: {entity_time:.2f}s")
                logger.info(f"Structured data extraction time: {structured_time:.2f}s")
                logger.info(f"Total time: {total_time:.2f}s")
                logger.info(f"Found {len(entities)} entities")
            
            # Calculate average metrics
            avg_entity_time = statistics.mean([r['entity_time'] for r in text_results])
            avg_structured_time = statistics.mean([r['structured_time'] for r in text_results])
            avg_total_time = statistics.mean([r['total_time'] for r in text_results])
            avg_num_entities = statistics.mean([r['num_entities'] for r in text_results])
            
            results[f"text_{i + 1}"] = {
                'runs': text_results,
                'avg_entity_time': avg_entity_time,
                'avg_structured_time': avg_structured_time,
                'avg_total_time': avg_total_time,
                'avg_num_entities': avg_num_entities,
                'text_length': len(text)
            }
            
            logger.info(f"Average entity extraction time: {avg_entity_time:.2f}s")
            logger.info(f"Average structured data extraction time: {avg_structured_time:.2f}s")
            logger.info(f"Average total time: {avg_total_time:.2f}s")
        
        return results
    
    except Exception as e:
        logger.error(f"Error benchmarking NER: {str(e)}")
        return None

def benchmark_pipeline(audio_files, num_runs=3):
    """Benchmark the complete processing pipeline."""
    logger.info(f"Benchmarking pipeline with {len(audio_files)} audio files, {num_runs} runs each")
    
    try:
        from core_engine.processing_pipeline import get_pipeline
        
        # Get the pipeline
        pipeline = get_pipeline()
        
        results = {}
        
        for audio_file in audio_files:
            logger.info(f"Testing file: {audio_file}")
            file_results = []
            
            for run in range(num_runs):
                logger.info(f"Run {run + 1}/{num_runs}")
                
                # Process the audio file
                start_time = time.time()
                result = pipeline.process_audio(audio_file)
                end_time = time.time()
                
                # Calculate metrics
                processing_time = end_time - start_time
                audio_duration = result.audio_duration
                rtf = processing_time / audio_duration
                
                file_results.append({
                    'processing_time': processing_time,
                    'audio_duration': audio_duration,
                    'rtf': rtf,
                    'num_entities': len(result.entities)
                })
                
                logger.info(f"Processing time: {processing_time:.2f}s")
                logger.info(f"Audio duration: {audio_duration:.2f}s")
                logger.info(f"Real-time factor: {rtf:.2f}x")
                logger.info(f"Found {len(result.entities)} entities")
            
            # Calculate average metrics
            avg_processing_time = statistics.mean([r['processing_time'] for r in file_results])
            avg_rtf = statistics.mean([r['rtf'] for r in file_results])
            avg_num_entities = statistics.mean([r['num_entities'] for r in file_results])
            
            results[os.path.basename(audio_file)] = {
                'runs': file_results,
                'avg_processing_time': avg_processing_time,
                'avg_rtf': avg_rtf,
                'avg_num_entities': avg_num_entities,
                'audio_duration': file_results[0]['audio_duration']
            }
            
            logger.info(f"Average processing time: {avg_processing_time:.2f}s")
            logger.info(f"Average real-time factor: {avg_rtf:.2f}x")
        
        return results
    
    except Exception as e:
        logger.error(f"Error benchmarking pipeline: {str(e)}")
        return None

def benchmark_parallel_processing(audio_files, max_workers=None):
    """Benchmark parallel processing of multiple audio files."""
    logger.info(f"Benchmarking parallel processing with {len(audio_files)} audio files")
    
    try:
        from core_engine.processing_pipeline import get_pipeline
        
        # Get the pipeline
        pipeline = get_pipeline()
        
        # Process files in parallel
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(pipeline.process_audio, audio_file): audio_file for audio_file in audio_files}
            results = {}
            
            for future in concurrent.futures.as_completed(future_to_file):
                audio_file = future_to_file[future]
                try:
                    result = future.result()
                    results[os.path.basename(audio_file)] = {
                        'processing_time': result.processing_time,
                        'audio_duration': result.audio_duration,
                        'rtf': result.processing_time / result.audio_duration,
                        'num_entities': len(result.entities)
                    }
                    logger.info(f"Processed {audio_file}: {result.processing_time:.2f}s, RTF: {result.processing_time / result.audio_duration:.2f}x")
                except Exception as e:
                    logger.error(f"Error processing {audio_file}: {str(e)}")
        
        total_time = time.time() - start_time
        total_audio_duration = sum([r['audio_duration'] for r in results.values()])
        overall_rtf = total_time / total_audio_duration
        
        logger.info(f"Total processing time: {total_time:.2f}s")
        logger.info(f"Total audio duration: {total_audio_duration:.2f}s")
        logger.info(f"Overall real-time factor: {overall_rtf:.2f}x")
        
        return {
            'files': results,
            'total_time': total_time,
            'total_audio_duration': total_audio_duration,
            'overall_rtf': overall_rtf
        }
    
    except Exception as e:
        logger.error(f"Error benchmarking parallel processing: {str(e)}")
        return None

def plot_results(results, title, output_file=None):
    """Plot benchmark results."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        plt.figure(figsize=(12, 6))
        
        if 'files' in results:
            # Parallel processing results
            files = list(results['files'].keys())
            rtfs = [results['files'][f]['rtf'] for f in files]
            
            plt.bar(files, rtfs)
            plt.axhline(y=results['overall_rtf'], color='r', linestyle='-', label=f"Overall RTF: {results['overall_rtf']:.2f}x")
            plt.ylabel('Real-time Factor (RTF)')
            plt.xlabel('Audio Files')
            plt.title(f"{title} - Overall RTF: {results['overall_rtf']:.2f}x")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.legend()
        
        else:
            # Individual component results
            files = list(results.keys())
            rtfs = [results[f]['avg_rtf'] for f in files]
            
            plt.bar(files, rtfs)
            plt.axhline(y=np.mean(rtfs), color='r', linestyle='-', label=f"Average RTF: {np.mean(rtfs):.2f}x")
            plt.ylabel('Real-time Factor (RTF)')
            plt.xlabel('Audio Files')
            plt.title(f"{title} - Average RTF: {np.mean(rtfs):.2f}x")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.legend()
        
        if output_file:
            plt.savefig(output_file)
            logger.info(f"Plot saved to {output_file}")
        else:
            plt.show()
    
    except Exception as e:
        logger.error(f"Error plotting results: {str(e)}")

def get_sample_texts():
    """Get sample texts for benchmarking."""
    return [
        "Наблюдение за тигрицей-багирой. Животное проявляет нормальную активность. Съело примерно 4 кг мяса из утренней порции. Температура воздуха 22 градуса. Поведение спокойное. После кормления легла отдыхать в тени. Состояние здоровья в норме.",
        "Питон Змей Горыныч. Длина 4 метра 30 сантиметров. Вес 42 килограмма. Температура 28 градусов. Вчера покормили, дали кролика весом 2,5 килограмма. Переваривает.",
        "Игуана Годзилла. Длина с хвостом 1 метр 65 сантиметров. Вес 6,3 килограмма. Температура тела 35 градусов. Съела 300 грамм салата, 200 грамм фруктов.",
        "Черепаха тортила. Диаметр панцира 78 сантиметров. Вес 95 килограмм. Очень старая. Возраст около 80 лет. Двигается медленно. Съела 1,5 килограмма травы и овощей. Углаженность в террариуме поддерживаем на уровне 70 процентов. Температура воздуха 26-28 градусов. Все показатели в норме."
    ]

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Benchmark Zoo Assistant performance')
    parser.add_argument('--component', choices=['asr', 'ner', 'pipeline', 'parallel'], default='pipeline',
                        help='Component to benchmark (default: pipeline)')
    parser.add_argument('--audio-dir', help='Directory containing audio files for testing')
    parser.add_argument('--num-runs', type=int, default=3, help='Number of runs for each test (default: 3)')
    parser.add_argument('--max-workers', type=int, help='Maximum number of workers for parallel processing')
    parser.add_argument('--plot', action='store_true', help='Plot results')
    parser.add_argument('--output', help='Output file for plot')
    
    args = parser.parse_args()
    
    # Get audio files
    audio_files = []
    if args.audio_dir:
        if not os.path.exists(args.audio_dir):
            logger.error(f"Audio directory not found: {args.audio_dir}")
            sys.exit(1)
        
        for root, _, files in os.walk(args.audio_dir):
            for file in files:
                if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                    audio_files.append(os.path.join(root, file))
    
    # Run benchmarks
    if args.component == 'asr':
        if not audio_files:
            logger.error("Audio files are required for ASR benchmarking")
            sys.exit(1)
        
        results = benchmark_asr(audio_files, args.num_runs)
        
        if args.plot and results:
            plot_results(results, "ASR Benchmark", args.output)
    
    elif args.component == 'ner':
        texts = get_sample_texts()
        results = benchmark_ner(texts, args.num_runs)
        
        if results:
            logger.info("NER Benchmark Results:")
            for text_id, text_results in results.items():
                logger.info(f"{text_id}:")
                logger.info(f"  Text length: {text_results['text_length']} characters")
                logger.info(f"  Average entity extraction time: {text_results['avg_entity_time']:.2f}s")
                logger.info(f"  Average structured data extraction time: {text_results['avg_structured_time']:.2f}s")
                logger.info(f"  Average total time: {text_results['avg_total_time']:.2f}s")
                logger.info(f"  Average number of entities: {text_results['avg_num_entities']:.1f}")
    
    elif args.component == 'pipeline':
        if not audio_files:
            logger.error("Audio files are required for pipeline benchmarking")
            sys.exit(1)
        
        results = benchmark_pipeline(audio_files, args.num_runs)
        
        if args.plot and results:
            plot_results(results, "Pipeline Benchmark", args.output)
    
    elif args.component == 'parallel':
        if not audio_files:
            logger.error("Audio files are required for parallel processing benchmarking")
            sys.exit(1)
        
        results = benchmark_parallel_processing(audio_files, args.max_workers)
        
        if args.plot and results:
            plot_results(results, "Parallel Processing Benchmark", args.output)

if __name__ == '__main__':
    main()