#!/usr/bin/env python3
"""
Media processor that integrates Factory and Strategy patterns
"""

from typing import Dict, List, Optional, Callable
from pathlib import Path
from media_handlers import MediaHandlerFactory, MediaHandler
from process_strategies import ProcessStrategy, ConvertStrategy, SplitStrategy, BatchProcessStrategy


class MediaProcessor:
    """Central media processor using Factory and Strategy patterns"""

    def __init__(self):
        """Initialize processor with factory"""
        self.factory = MediaHandlerFactory()
        self.current_strategy = None
        self.current_handler = None
        self.last_info = None

    def set_strategy(self, strategy: ProcessStrategy):
        """Set the processing strategy"""
        self.current_strategy = strategy
        return self

    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """Get file information using appropriate handler"""
        handler = self.factory.create_handler(file_path)
        if handler:
            self.current_handler = handler
            self.last_info = handler.get_info(file_path)
            return self.last_info
        return None

    def process_file(self, file_path: str, output_params: Dict = None) -> bool:
        """Process a single file with current strategy"""
        if not self.current_strategy:
            raise ValueError("No processing strategy set")

        # Ensure we have a handler for this file
        if not self.current_handler or not self.current_handler.can_handle(file_path):
            handler = self.factory.create_handler(file_path)
            if not handler:
                return False
            self.current_handler = handler

        # Get file info if not already cached
        if not self.last_info or self.last_info.get('path') != file_path:
            self.last_info = self.current_handler.get_info(file_path)

        # Execute strategy
        output_params = output_params or {}
        return self.current_strategy.execute(file_path, output_params)

    def process_batch(self, file_paths: List[str], output_params: Dict = None,
                     progress_callback: Callable = None) -> List[bool]:
        """Process multiple files with current strategy"""
        if not self.current_strategy:
            raise ValueError("No processing strategy set")

        results = []
        total = len(file_paths)

        for i, file_path in enumerate(file_paths):
            # Check if file is supported
            if not self.factory.is_supported(file_path):
                results.append(False)
                if progress_callback:
                    progress_callback(i + 1, total, Path(file_path).name, False)
                continue

            # Process file
            result = self.process_file(file_path, output_params)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, total, Path(file_path).name, result)

        return results

    def is_supported(self, file_path: str) -> bool:
        """Check if file is supported"""
        return self.factory.is_supported(file_path)

    def get_supported_formats(self, media_type: str = 'all') -> set:
        """Get supported formats"""
        return self.factory.get_supported_formats(media_type)


class MediaProcessorBuilder:
    """Builder class for creating configured MediaProcessor instances"""

    @staticmethod
    def create_converter(format: str, bitrate: str = '192k',
                        sample_rate: str = '44100', normalize: bool = False, **kwargs) -> MediaProcessor:
        """Create a processor configured for conversion"""
        processor = MediaProcessor()
        options = {
            'bitrate': bitrate,
            'sample_rate': sample_rate,
            'normalize': normalize
        }
        options.update(kwargs)  # Add any additional options

        strategy = ConvertStrategy(
            target_format=format,
            options=options
        )
        processor.set_strategy(strategy)
        return processor

    @staticmethod
    def create_splitter(mode: str, **kwargs) -> MediaProcessor:
        """Create a processor configured for splitting"""
        processor = MediaProcessor()

        if mode == 'duration':
            params = {'duration': kwargs.get('duration', 300)}
        elif mode == 'size':
            params = {'size': kwargs.get('size', 100)}
        elif mode == 'parts':
            params = {'parts': kwargs.get('parts', 2)}
        else:
            raise ValueError(f"Unknown split mode: {mode}")

        strategy = SplitStrategy(split_mode=mode, split_params=params)
        processor.set_strategy(strategy)
        return processor

    @staticmethod
    def create_batch_converter(format: str, **options) -> MediaProcessor:
        """Create a processor for batch conversion"""
        processor = MediaProcessor()
        convert_strategy = ConvertStrategy(target_format=format, options=options)
        batch_strategy = BatchProcessStrategy(convert_strategy)
        processor.set_strategy(batch_strategy)
        return processor

    @staticmethod
    def create_batch_splitter(mode: str, **params) -> MediaProcessor:
        """Create a processor for batch splitting"""
        processor = MediaProcessor()
        split_strategy = SplitStrategy(split_mode=mode, split_params=params)
        batch_strategy = BatchProcessStrategy(split_strategy)
        processor.set_strategy(batch_strategy)
        return processor


# Example usage functions
def convert_audio_file(input_file: str, output_format: str = 'mp3',
                       bitrate: str = '192k', output_dir: str = None) -> bool:
    """Convenience function to convert a single audio file"""
    processor = MediaProcessorBuilder.create_converter(
        format=output_format,
        bitrate=bitrate
    )

    output_params = {}
    if output_dir:
        output_params['output_dir'] = output_dir

    return processor.process_file(input_file, output_params)


def split_media_file(input_file: str, mode: str = 'duration',
                    duration: int = 300, keep_original: bool = False) -> bool:
    """Convenience function to split a single media file"""
    processor = MediaProcessorBuilder.create_splitter(
        mode=mode,
        duration=duration
    )

    output_params = {'keep_original': keep_original}
    return processor.process_file(input_file, output_params)


def batch_convert_files(input_files: List[str], output_format: str = 'mp3',
                       progress_callback: Callable = None) -> List[bool]:
    """Convenience function for batch conversion"""
    processor = MediaProcessorBuilder.create_batch_converter(format=output_format)
    return processor.process_batch(input_files, progress_callback=progress_callback)


def batch_split_files(input_files: List[str], mode: str = 'duration',
                     duration: int = 300, progress_callback: Callable = None) -> List[bool]:
    """Convenience function for batch splitting"""
    processor = MediaProcessorBuilder.create_batch_splitter(
        mode=mode,
        duration=duration
    )
    return processor.process_batch(input_files, progress_callback=progress_callback)