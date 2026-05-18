import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BasePdfToolComponent } from '../base-pdf-tool.component';
import { HttpEvent, HttpEventType } from '@angular/common/http';

@Component({
  selector: 'app-remove-pages',
  imports: [CommonModule, FormsModule],
  templateUrl: './remove-pages.component.html',
  styleUrl: './remove-pages.component.css',
  standalone: true
})
export class RemovePagesComponent extends BasePdfToolComponent {
  toolId = 'remove-pages';
  
  pagesToRemove: string = '';

  override convert(): void {
    if (!this.selectedFile && !this.fileKey) {
        this.toastService.show('Please select a file first', 'error');
        return;
    }

    if (!this.pagesToRemove.trim()) {
        this.toastService.show('Please specify the pages to remove', 'error');
        return;
    }

    this.isConverting = true;
    this.conversionResult = null;
    this.uploadProgress = 0;
    this.conversionStatus = 'Uploading...';
    this.startProgressSimulation(0, 85);

    const extraParams = {
        pages_to_remove: this.pagesToRemove
    };

    this.pdfService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, this.fileKey, extraParams)
        .subscribe({
            next: (event: HttpEvent<any>) => {
                switch (event.type) {
                    case HttpEventType.Sent:
                        this.conversionStatus = 'Uploading...';
                        break;
                    case HttpEventType.UploadProgress:
                        if (event.total) {
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
                        this.isConverting = false;
                        if (event.body && event.body.success) {
                            const response = event.body;
                            this.toastService.show('Pages removed successfully', 'success');
                            
                            if (response && response.download_url) {
                                this.conversionResult = {
                                    downloadUrl: response.download_url,
                                    fileName: response.output_filename || 'modified_document.pdf'
                                };
                            } else {
                                this.toastService.show('Conversion failed: No download URL returned', 'error');
                            }
                        } else {
                            this.toastService.show('Conversion failed', 'error');
                        }
                        break;
                }
            },
            error: (error) => {
                this.stopProgressSimulation(0);
                this.isConverting = false;
                this.uploadProgress = 0;
                this.conversionStatus = '';
                console.error('Conversion error:', error);
                this.toastService.show(this.buildPageErrorMessage(error, 'remove'), 'error');
            }
        });
  }

  override reset(): void {
      super.reset();
      this.pagesToRemove = '';
  }

  onFileChange(event: any): void {
      const file = event.target?.files?.[0];
      if (file) {
          this.onFileSelected(file);
      }
      // Reset input so the same file (or any file) can be re-selected after reset
      event.target.value = '';
  }

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  private buildPageErrorMessage(error: any, action: 'remove' | 'extract'): string {
    const body = error?.error;
    // FastAPI serializes HTTPException detail as: { detail: { error_type, message, details: {...} } }
    const detail = body?.detail;
    const totalPages: number | undefined = detail?.details?.total_pages;
    const invalidPages: number[] | undefined = detail?.details?.invalid_pages;

    if (totalPages !== undefined && invalidPages && invalidPages.length > 0) {
      const sorted = [...invalidPages].sort((a, b) => a - b);
      const pageWord = sorted.length === 1 ? 'Page' : 'Pages';
      const pageList = sorted.join(', ');
      const verb = action === 'remove' ? 'remove' : 'extract';
      return `This PDF has ${totalPages} page${totalPages !== 1 ? 's' : ''}. ` +
             `${pageWord} ${pageList} do${sorted.length === 1 ? 'es' : ''} not exist. ` +
             `You can only ${verb} pages 1\u2013${totalPages}.`;
    }

    return detail?.message || body?.message || error?.message || 'An error occurred during conversion.';
  }
}
