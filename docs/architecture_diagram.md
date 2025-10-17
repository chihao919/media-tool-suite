# 檔案豪幫手 - 系統架構圖

## 1. 系統分層架構圖

```
┌──────────────────────────────────────────────────────────────┐
│                     Presentation Layer (UI)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          audio_converter_tabbed.py                    │   │
│  │  ┌─────────┬──────────┬──────────┬─────────────┐    │   │
│  │  │ Convert │  Split   │ Settings │   History    │    │   │
│  │  │   Tab   │   Tab    │   Tab    │     Tab      │    │   │
│  │  └─────────┴──────────┴──────────┴─────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              media_processor.py                       │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  MediaProcessor    MediaProcessorBuilder     │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                        ┌─────┴─────┐                         │
│            ┌───────────▼───┐   ┌───▼───────────┐            │
│            │ Factory Layer │   │ Strategy Layer │            │
│            └───────────────┘   └───────────────┘            │
└──────────────────────────────────────────────────────────────┘
                    │                    │
        ┌───────────▼────────┐  ┌───────▼────────┐
        │ media_handlers.py  │  │process_strategies│
        │                    │  │      .py         │
        │ ┌────────────────┐ │  │ ┌──────────────┐│
        │ │ AudioHandler   │ │  │ │ConvertStrategy││
        │ │ VideoHandler   │ │  │ │ SplitStrategy ││
        │ │HandlerFactory  │ │  │ │BatchStrategy  ││
        │ └────────────────┘ │  │ └──────────────┘│
        └────────────────────┘  └──────────────────┘
                    │                    │
                    └─────────┬──────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                     Data/Config Layer                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 app_constants.py                      │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ AppConstants                                   │  │   │
│  │  │ - AUDIO_EXTENSIONS  - DEFAULT_SETTINGS        │  │   │
│  │  │ - VIDEO_EXTENSIONS  - CODEC_MAP               │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    External Dependencies                      │
│         ┌─────────┐  ┌─────────┐  ┌─────────────┐           │
│         │ FFmpeg  │  │ FFprobe │  │ File System │           │
│         └─────────┘  └─────────┘  └─────────────┘           │
└──────────────────────────────────────────────────────────────┘
```

## 2. UML 類別圖

```mermaid
classDiagram
    %% Abstract Classes
    class MediaHandler {
        <<abstract>>
        +can_handle(file_path: str) bool
        +get_info(file_path: str) dict
        +get_duration(file_path: str) float
        +get_file_size(file_path: str) int
        +get_format_info(file_path: str) dict
    }

    class ProcessStrategy {
        <<abstract>>
        +execute(input_file: str, output_params: dict) bool
        #run_ffmpeg_command(cmd: list) tuple
    }

    %% Concrete Handlers
    class AudioHandler {
        -SUPPORTED_FORMATS: set
        +can_handle(file_path: str) bool
        +get_info(file_path: str) dict
    }

    class VideoHandler {
        -SUPPORTED_FORMATS: set
        +can_handle(file_path: str) bool
        +get_info(file_path: str) dict
    }

    %% Factory
    class MediaHandlerFactory {
        -_handlers: list
        +create_handler(file_path: str) MediaHandler
        +get_supported_formats(media_type: str) set
        +is_supported(file_path: str) bool
    }

    %% Concrete Strategies
    class ConvertStrategy {
        -target_format: str
        -options: dict
        +execute(input_file: str, output_params: dict) bool
        -_generate_output_filename(input_file: str, output_params: dict) str
        -_build_convert_command(input_file: str, output_file: str) list
    }

    class SplitStrategy {
        -split_mode: str
        -split_params: dict
        +execute(input_file: str, output_params: dict) bool
        -_split_by_duration(input_file: str, output_params: dict) bool
        -_split_by_size(input_file: str, output_params: dict) bool
        -_split_by_parts(input_file: str, output_params: dict) bool
        -_perform_split(input_file: str, output_params: dict, num_parts: int, part_duration: float, total_duration: float) bool
    }

    class BatchProcessStrategy {
        -strategy: ProcessStrategy
        +execute(input_file: str, output_params: dict) bool
        +execute_batch(input_files: list, output_params: dict, progress_callback: callable) list
    }

    %% Processor
    class MediaProcessor {
        -factory: MediaHandlerFactory
        -current_strategy: ProcessStrategy
        -current_handler: MediaHandler
        -last_info: dict
        +set_strategy(strategy: ProcessStrategy) MediaProcessor
        +get_file_info(file_path: str) dict
        +process_file(file_path: str, output_params: dict) bool
        +process_batch(file_paths: list, output_params: dict, progress_callback: callable) list
        +is_supported(file_path: str) bool
        +get_supported_formats(media_type: str) set
    }

    class MediaProcessorBuilder {
        <<static>>
        +create_converter(format: str, bitrate: str, sample_rate: str, normalize: bool)$ MediaProcessor
        +create_splitter(mode: str, kwargs: dict)$ MediaProcessor
        +create_batch_converter(format: str, options: dict)$ MediaProcessor
        +create_batch_splitter(mode: str, params: dict)$ MediaProcessor
    }

    %% Constants
    class AppConstants {
        <<static>>
        +APP_NAME: str
        +APP_VERSION: str
        +AUDIO_EXTENSIONS: set
        +VIDEO_EXTENSIONS: set
        +MEDIA_EXTENSIONS: set
        +BITRATE_OPTIONS: list
        +AUDIO_FORMAT_OPTIONS: list
        +VIDEO_FORMAT_OPTIONS: list
        +SAMPLE_RATE_OPTIONS: list
        +SPLIT_MODE_OPTIONS: list
        +DEFAULT_SETTINGS: dict
        +CODEC_MAP: dict
        +get_file_filter(media_type: str)$ list
        +is_supported_format(file_path: str, media_type: str)$ bool
        +get_codec_for_format(format_name: str)$ str
    }

    %% UI Class
    class TabbedAudioConverter {
        -root: tk.Tk
        -convert_files: list
        -split_files: list
        -output_format: tk.StringVar
        -bitrate: tk.StringVar
        -sample_rate: tk.StringVar
        -normalize: tk.BooleanVar
        -split_mode: tk.StringVar
        -split_duration: tk.StringVar
        -split_size: tk.StringVar
        -keep_original: tk.BooleanVar
        -conversion_history: list
        -split_history: list
        +setup_convert_tab()
        +setup_split_tab()
        +setup_settings_tab()
        +setup_history_tab()
        +add_files(tab: str)
        +add_folder(tab: str)
        +clear_files(tab: str)
        +convert_files()
        +split_files_action()
        -_convert_worker(custom_output_dir: str)
        -_split_worker()
        -_split_single_file(file_path: str)
        +apply_all_settings()
        +reset_to_defaults()
        +save_settings()
        +load_settings()
        +add_conversion_history(filename: str, from_format: str, to_format: str, success: bool)
        +add_split_history(filename: str, mode: str, value: str, parts_created: int, success: bool)
        +update_statistics()
        +clear_history()
    }

    %% Relationships
    MediaHandler <|-- AudioHandler : inherits
    MediaHandler <|-- VideoHandler : inherits
    ProcessStrategy <|-- ConvertStrategy : inherits
    ProcessStrategy <|-- SplitStrategy : inherits
    ProcessStrategy <|-- BatchProcessStrategy : inherits

    MediaHandlerFactory "1" o-- "*" MediaHandler : creates
    MediaProcessor "1" o-- "1" MediaHandlerFactory : uses
    MediaProcessor "1" o-- "0..1" ProcessStrategy : uses
    MediaProcessor "1" o-- "0..1" MediaHandler : uses

    BatchProcessStrategy "1" o-- "1" ProcessStrategy : wraps

    MediaProcessorBuilder ..> MediaProcessor : creates
    MediaProcessorBuilder ..> ConvertStrategy : creates
    MediaProcessorBuilder ..> SplitStrategy : creates
    MediaProcessorBuilder ..> BatchProcessStrategy : creates

    TabbedAudioConverter ..> AppConstants : uses
    TabbedAudioConverter ..> MediaProcessor : uses
    TabbedAudioConverter ..> MediaProcessorBuilder : uses

    ConvertStrategy ..> AppConstants : uses
    AudioHandler ..> AppConstants : uses
    VideoHandler ..> AppConstants : uses
```

## 3. 設計模式關係圖

```
┌─────────────────────────────────────────────────────────┐
│                    Factory Pattern                        │
│                                                           │
│  Client Request ──► MediaHandlerFactory                  │
│                            │                             │
│                            ▼                             │
│                   Check file extension                   │
│                            │                             │
│                ┌───────────┴───────────┐                │
│                ▼                       ▼                │
│         AudioHandler            VideoHandler             │
│         (.mp3,.wav...)          (.mp4,.avi...)         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Strategy Pattern                        │
│                                                           │
│   MediaProcessor                                         │
│        │                                                 │
│        ├─► set_strategy(ConvertStrategy)                │
│        │        └─► execute() ──► Convert File          │
│        │                                                 │
│        ├─► set_strategy(SplitStrategy)                  │
│        │        └─► execute() ──► Split File            │
│        │                                                 │
│        └─► set_strategy(BatchProcessStrategy)           │
│                 └─► execute() ──► Process Multiple      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    Builder Pattern                        │
│                                                           │
│   MediaProcessorBuilder                                  │
│        │                                                 │
│        ├─► create_converter()    ──► MediaProcessor     │
│        │                              + ConvertStrategy  │
│        │                                                 │
│        ├─► create_splitter()     ──► MediaProcessor     │
│        │                              + SplitStrategy    │
│        │                                                 │
│        └─► create_batch_*()      ──► MediaProcessor     │
│                                       + BatchStrategy    │
└─────────────────────────────────────────────────────────┘
```

## 4. 資料流程圖

```
User Input (GUI)
      │
      ▼
TabbedAudioConverter
      │
      ├──► Select Files
      │
      ├──► Choose Operation (Convert/Split)
      │
      ▼
MediaProcessorBuilder
      │
      ├──► Create appropriate processor
      │
      ▼
MediaProcessor
      │
      ├──► MediaHandlerFactory.create_handler()
      │         │
      │         └──► Get file info
      │
      ├──► ProcessStrategy.execute()
      │         │
      │         └──► Run FFmpeg commands
      │
      ▼
Output Files + Update GUI
```

## 5. 模組依賴關係

```
                    ┌─────────────────────┐
                    │ audio_converter_    │
                    │    tabbed.py        │
                    └──────────┬──────────┘
                               │ depends on
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌──────────┐  ┌──────────────┐  ┌──────────┐
        │   app_   │  │    media_    │  │  media_  │
        │constants │  │  processor   │  │ handlers │
        └──────────┘  └──────┬───────┘  └──────────┘
                              │ depends on
                    ┌─────────┴──────────┐
                    ▼                    ▼
            ┌──────────────┐    ┌──────────────┐
            │   process_   │    │    media_     │
            │  strategies  │    │   handlers    │
            └──────────────┘    └──────────────┘
                    │                    │
                    └─────────┬──────────┘
                              ▼
                      ┌──────────────┐
                      │     app_     │
                      │  constants   │
                      └──────────────┘
```