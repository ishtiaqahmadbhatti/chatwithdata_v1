import { Component, inject } from '@angular/core';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { MarkdownConversionService } from '../../../app_services/markdown_conversion.service';
import { ToastService } from '../../../app_services/toast';

@Component({
    template: ''
})
export abstract class BaseMarkdownToolComponent {
    protected markdownService = inject(MarkdownConversionService);
    protected toastService = inject(ToastService);

    abstract toolId: string;

    selectedFile: File | null = null;
    outputFilename: string = '';
    fileKey: string = '';
    isConverting: boolean = false;
    conversionStatus: string = '';
    conversionResult: { downloadUrl: string, fileName: string } | null = null;

    onFileSelected(file: File): void {
        if (file) {
            this.selectedFile = file;
            this.fileKey = '';
            const nameWithoutExt = file.name.substring(0, file.name.lastIndexOf('.'));
            this.outputFilename = nameWithoutExt;
            this.conversionResult = null;
            this.conversionStatus = '';
        }
    }

    convert(): void {
        if (!this.selectedFile && !this.fileKey) {
            this.toastService.show('Please select a file first', 'error');
            return;
        }

        this.isConverting = true;
        this.conversionResult = null;
        this.conversionStatus = 'Initializing...';

        this.markdownService.convertFile(this.toolId, this.selectedFile, this.outputFilename, this.fileKey)
            .subscribe({
                next: (event: HttpEvent<any>) => {
                    switch (event.type) {
                        case HttpEventType.Sent:
                            this.conversionStatus = 'Request sent...';
                            break;
                        case HttpEventType.UploadProgress:
                            // Handle progress if needed, though markdown files are small
                            break;
                        case HttpEventType.Response:
                            const response = event.body;
                            if (response && response.success && response.download_url) {
                                this.conversionResult = {
                                    downloadUrl: response.download_url,
                                    fileName: response.output_filename || 'converted_result'
                                };
                                this.isConverting = false;
                                this.conversionStatus = '✅ Done!';
                                this.toastService.show(response.message || 'File converted successfully.', 'success');
                            } else {
                                this.toastService.show('Conversion failed.', 'error');
                                this.isConverting = false;
                                this.conversionStatus = '❌ Failed';
                            }
                            break;
                    }
                },
                error: (error) => {
                    console.error('Conversion failed', error);
                    this.conversionStatus = '❌ Conversion failed. Please try again.';
                    this.toastService.show('Conversion failed. Please try again.', 'error');
                    this.isConverting = false;
                }
            });
    }

    saveFile(): void {
        if (!this.conversionResult) return;
        this.markdownService.downloadFile(this.conversionResult.fileName).subscribe({
            next: (blob) => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = this.conversionResult!.fileName;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                this.toastService.show('File saved successfully!', 'success');
                this.reset();
            },
            error: (err) => {
                console.error('Download failed', err);
                this.toastService.show('Download failed. Please try again.', 'error');
            }
        });
    }

    reset(): void {
        this.selectedFile = null;
        this.outputFilename = '';
        this.isConverting = false;
        this.conversionResult = null;
        this.conversionStatus = '';
    }
}
