import { Component, inject } from '@angular/core';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { FileFormatterService } from '../../../app_services/file_formatter.service';
import { ToastService } from '../../../app_services/toast';

@Component({
    template: ''
})
export abstract class BaseFileFormatterToolComponent {
    // Services
    protected formatterService = inject(FileFormatterService);
    protected toastService = inject(ToastService);

    // Configuration - Abstract property that child classes must implement
    abstract toolId: string;

    // State
    selectedFile: File | null = null;
    outputFilename: string = '';
    fileKey: string = '';
    isConverting: boolean = false;
    uploadProgress: number = 0;
    conversionStatus: string = '';
    conversionResult: { downloadUrl: string, fileName: string } | null = null;

    onFileSelected(file: File): void {
        if (file) {
            this.selectedFile = file;
            this.fileKey = '';
            // Auto-suggest filename without extension
            const nameWithoutExt = file.name.substring(0, file.name.lastIndexOf('.'));
            this.outputFilename = nameWithoutExt;

            this.conversionResult = null; // Reset result on new file selection
            this.uploadProgress = 0;
            this.conversionStatus = '';
            this.toastService.show('File selected successfully', 'success');
        }
    }

    convert(): void {
        if (!this.selectedFile && !this.fileKey) {
            this.toastService.show('Please select a file first', 'error');
            return;
        }

        this.isConverting = true;
        this.conversionResult = null;
        this.uploadProgress = 0;
        this.conversionStatus = 'Initializing...';

        // IMPORTANT: The backend for file formatter might expect slightly different endpoints naming convention
        // defaulting to using the toolId which usually matches the endpoint slug
        this.formatterService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, this.fileKey)
            .subscribe({
                next: (event: HttpEvent<any>) => {
                    switch (event.type) {
                        case HttpEventType.Sent:
                            this.conversionStatus = 'Request sent...';
                            break;
                        case HttpEventType.UploadProgress:
                            if (event.total) {
                                this.uploadProgress = Math.round(100 * event.loaded / event.total);
                            } else {
                                this.uploadProgress = 50;
                            }
                            this.conversionStatus = `File Uploading... ${this.uploadProgress}%`;
                            break;

                        case HttpEventType.Response:
                            this.uploadProgress = 100;
                            this.conversionStatus = 'Processing...';
                            setTimeout(() => {
                                const response = event.body;
                                if (response && response.download_url) {
                                    this.conversionResult = {
                                        downloadUrl: response.download_url,
                                        fileName: response.output_filename || 'formatted_result'
                                    };
                                    this.isConverting = false;
                                    this.toastService.show('File formatted successfully. Ready to save.', 'success');
                                } else if (response && (response.message || response.is_valid !== undefined)) {
                                    // Some formatter tools like validation might not return a file download but a status
                                    // Adapt as needed, for now assuming download flow or checking message
                                    if (response.download_url) {
                                        this.conversionResult = {
                                            downloadUrl: response.download_url,
                                            fileName: response.output_filename || 'result'
                                        };
                                        this.isConverting = false;
                                        this.toastService.show('Operation successful.', 'success');
                                    } else {
                                        // Handle validation results that are just text/json
                                        this.isConverting = false;
                                        this.conversionStatus = 'Completed';
                                        this.toastService.show(response.message || 'Operation successful', 'success');
                                        // potentially show result in UI, but for now we stick to common pattern
                                    }
                                } else {
                                    this.toastService.show('Operation failed: No result returned.', 'error');
                                    this.isConverting = false;
                                    this.conversionStatus = '❌ Failed';
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

    saveFile(): void {
        if (!this.conversionResult) return;
        this.formatterService.downloadFile(this.conversionResult.downloadUrl).subscribe({
            next: (blob) => {
                this.downloadBlob(blob, this.conversionResult!.fileName);
                this.toastService.show('File saved successfully!', 'success');
                this.reset();
            },
            error: (err) => {
                console.error('Download failed', err);
                this.toastService.show('Download failed. Please try again.', 'error');
            }
        });
    }

    protected handleError(error: any): void {
        console.error('Operation failed', error);
        this.conversionStatus = '❌ Operation failed. Please try again.';
        this.toastService.show('Operation failed. Please try again.', 'error');
        this.isConverting = false;
    }

    protected downloadBlob(blob: Blob, filename: string): void {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    reset(): void {
        this.selectedFile = null;
        this.outputFilename = '';
        this.isConverting = false;
        this.conversionResult = null;
    }
}
