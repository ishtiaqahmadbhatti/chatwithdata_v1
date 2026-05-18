import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseAudioToolComponent } from '../base-audio-tool.component';

interface TranscriptionResult {
    text: string;
    language: string;
    confidence: string;
    word_count: number;
    character_count: number;
}

interface AudioToTextResponse {
    success: boolean;
    message: string;
    transcription: TranscriptionResult;
    output_filename: string;
    download_url: string;
}

@Component({
    selector: 'app-audio-to-text',
    imports: [CommonModule, FormsModule, FileConversionUiComponent],
    templateUrl: './audio-to-text.component.html',
    styleUrl: './audio-to-text.component.css',
    standalone: true
})
export class AudioToTextComponent extends BaseAudioToolComponent {
    toolId = 'audio-to-text';
    selectedLanguage: string = 'en-US';
    transcriptionResult: TranscriptionResult | null = null;

    // Language options
    languages = [
        { code: 'en-US', name: 'English (US)' },
        { code: 'en-GB', name: 'English (UK)' },
        { code: 'ur-PK', name: 'Urdu (Pakistan)' },
        { code: 'ar-SA', name: 'Arabic (Saudi Arabia)' },
        { code: 'es-ES', name: 'Spanish (Spain)' },
        { code: 'fr-FR', name: 'French (France)' },
        { code: 'de-DE', name: 'German (Germany)' },
        { code: 'it-IT', name: 'Italian (Italy)' },
        { code: 'pt-BR', name: 'Portuguese (Brazil)' },
        { code: 'ru-RU', name: 'Russian (Russia)' },
        { code: 'ja-JP', name: 'Japanese (Japan)' },
        { code: 'ko-KR', name: 'Korean (South Korea)' },
        { code: 'zh-CN', name: 'Chinese (Simplified)' },
        { code: 'hi-IN', name: 'Hindi (India)' },
        { code: 'tr-TR', name: 'Turkish (Turkey)' }
    ];

    override onFileSelected(file: File): void {
        super.onFileSelected(file);
        this.transcriptionResult = null;
    }

    override convert(): void {
        if (!this.selectedFile && !this.fileKey) {
            this.toastService.show('Please select an audio file first', 'error');
            return;
        }

        this.isConverting = true;
        this.transcriptionResult = null;
        this.conversionResult = null;
        this.uploadProgress = 0;
        this.conversionStatus = 'Initializing...';

        this.audioService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, { language: this.selectedLanguage }, this.fileKey)
            .subscribe({
                next: (event: HttpEvent<any>) => {
                    switch (event.type) {
                        case HttpEventType.Sent:
                            this.conversionStatus = 'Request sent...';
                            break;
                        case HttpEventType.UploadProgress:
                            if (event.total) {
                                this.uploadProgress = Math.round(100 * event.loaded / event.total);
                                this.conversionStatus = `Uploading... ${this.uploadProgress}%`;
                            }
                            break;
                        case HttpEventType.Response:
                            this.conversionStatus = 'Transcribing audio...';
                            setTimeout(() => {
                                const response: AudioToTextResponse = event.body;
                                if (response && response.success) {
                                    this.transcriptionResult = response.transcription;
                                    this.conversionResult = {
                                        downloadUrl: response.download_url,
                                        fileName: response.output_filename
                                    };
                                    this.isConverting = false;
                                    this.toastService.show('Audio transcribed successfully!', 'success');
                                } else {
                                    this.toastService.show('Transcription failed', 'error');
                                    this.isConverting = false;
                                    this.conversionStatus = 'Failed';
                                }
                            }, 500);
                            break;
                    }
                },
                error: (error) => {
                    this.handleError(error);
                }
            });
    }

    copyToClipboard(): void {
        if (!this.transcriptionResult) return;

        navigator.clipboard.writeText(this.transcriptionResult.text).then(() => {
            this.toastService.show('Text copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy text', err);
            this.toastService.show('Failed to copy text', 'error');
        });
    }

    override reset(): void {
        super.reset();
        this.selectedLanguage = 'en-US';
        this.transcriptionResult = null;
    }
}
