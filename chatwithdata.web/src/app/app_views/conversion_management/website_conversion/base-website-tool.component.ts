import { Component, inject } from '@angular/core';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { WebsiteConversionService } from '../../../app_services/website_conversion.service';
import { ToastService } from '../../../app_services/toast';

@Component({
    template: ''
})
export abstract class BaseWebsiteToolComponent {
    // Services
    protected websiteService = inject(WebsiteConversionService);
    protected toastService = inject(ToastService);

    // Configuration - Abstract property that child classes must implement
    abstract toolId: string;

    // State
    selectedFile: File | null = null;
    outputFilename: string = '';
    fileKey: string = '';
    url: string = '';
    content: string = '';
    isConverting: boolean = false;
    uploadProgress: number = 0;
    conversionStatus: string = '';
    conversionResult: { downloadUrl: string, fileName: string } | null = null;

    onFileSelected(file: File): void {
        if (file) {
            this.selectedFile = file;
            this.fileKey = '';
            this.url = '';
            this.content = '';
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
        if (!this.selectedFile && !this.fileKey && !this.url && !this.content) {
            this.toastService.show('Please provide a file, URL, or content first', 'error');
            return;
        }

        this.isConverting = true;
        this.conversionResult = null;
        this.uploadProgress = 0;
        this.conversionStatus = 'Initializing...';

        this.websiteService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, this.fileKey, this.url, this.content)
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
                            this.conversionStatus = 'File Converting...';
                            setTimeout(() => {
                                const response = event.body;
                                if (response && response.download_url) {
                                    this.conversionResult = {
                                        downloadUrl: response.download_url,
                                        fileName: response.output_filename || 'converted_result'
                                    };
                                    this.isConverting = false;
                                    this.conversionStatus = '✅ Done!';
                                    this.toastService.show('File converted successfully. Ready to save.', 'success');
                                } else {
                                    this.toastService.show('Conversion failed: No download URL returned.', 'error');
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
        this.websiteService.downloadFile(this.conversionResult.downloadUrl).subscribe({
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
        console.error('Conversion failed', error);
        this.conversionStatus = '❌ Conversion failed. Please try again.';
        this.toastService.show('Conversion failed. Please try again.', 'error');
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
        this.url = '';
        this.content = '';
        this.isConverting = false;
        this.conversionResult = null;
    }
}
