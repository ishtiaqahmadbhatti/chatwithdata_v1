import { Component, inject } from '@angular/core';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { PDFConversionService } from '../../../app_services/pdf_conversion.service';
import { ToastService } from '../../../app_services/toast';

@Component({
    template: ''
})
export abstract class BasePdfToolComponent {
    // Services
    protected pdfService = inject(PDFConversionService);
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

    // Internal progress simulation
    private _progressInterval: any = null;

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

    /** Start a simulated progress ticker from current progress up to maxProgress. */
    protected startProgressSimulation(startFrom: number = 0, maxProgress: number = 85): void {
        this.stopProgressSimulation();
        this.uploadProgress = startFrom;
        this._progressInterval = setInterval(() => {
            const remaining = maxProgress - this.uploadProgress;
            if (remaining <= 0) {
                this.stopProgressSimulation();
                return;
            }
            // Ease-out: moves fast at start, slows near max
            const step = Math.max(0.3, remaining * 0.04);
            this.uploadProgress = Math.min(maxProgress, Math.round((this.uploadProgress + step) * 10) / 10);
        }, 120);
    }

    /** Stop simulation and optionally snap to a final value. */
    protected stopProgressSimulation(finalValue?: number): void {
        if (this._progressInterval) {
            clearInterval(this._progressInterval);
            this._progressInterval = null;
        }
        if (finalValue !== undefined) {
            this.uploadProgress = finalValue;
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
        this.conversionStatus = 'Uploading...';
        this.startProgressSimulation(0, 85);

        this.pdfService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, this.fileKey)
            .subscribe({
                next: (event: HttpEvent<any>) => {
                    switch (event.type) {
                        case HttpEventType.Sent:
                            this.conversionStatus = 'Uploading...';
                            break;
                        case HttpEventType.UploadProgress:
                            if (event.total) {
                                // Real upload progress: allow up to 60% then server picks up
                                const realPct = Math.round(60 * event.loaded / event.total);
                                if (realPct > this.uploadProgress) {
                                    this.stopProgressSimulation();
                                    this.uploadProgress = realPct;
                                    this.startProgressSimulation(realPct, 85);
                                }
                            }
                            this.conversionStatus = `Uploading... ${this.uploadProgress}%`;
                            break;

                        case HttpEventType.ResponseHeader:
                            this.conversionStatus = 'Processing...';
                            break;

                        case HttpEventType.Response:
                            this.stopProgressSimulation(100);
                            this.conversionStatus = '✅ Done!';
                            setTimeout(() => {
                                const response = event.body;
                                if (response && response.download_url) {
                                    this.conversionResult = {
                                        downloadUrl: response.download_url,
                                        fileName: response.output_filename || 'converted_result'
                                    };
                                    this.isConverting = false;
                                    this.toastService.show('File converted successfully. Ready to save.', 'success');
                                } else {
                                    this.toastService.show('Conversion failed: No download URL returned.', 'error');
                                    this.isConverting = false;
                                    this.conversionStatus = '❌ Failed';
                                }
                            }, 400);
                            break;
                    }
                },
                error: (error) => {
                    this.stopProgressSimulation(0);
                    this.handleError(error);
                }
            });
    }

    saveFile(): void {
        if (!this.conversionResult) return;
        this.pdfService.downloadFile(this.conversionResult.downloadUrl).subscribe({
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
        this.stopProgressSimulation(0);
        this.selectedFile = null;
        this.outputFilename = '';
        this.isConverting = false;
        this.conversionResult = null;
        this.conversionStatus = '';
        this.uploadProgress = 0;
    }
}
