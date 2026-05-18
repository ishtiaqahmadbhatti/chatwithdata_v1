import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BasePdfToolComponent } from '../base-pdf-tool.component';
import { HttpEvent, HttpEventType } from '@angular/common/http';

@Component({
  selector: 'app-add-watermark',
  imports: [CommonModule, FormsModule],
  templateUrl: './add-watermark.component.html',
  styleUrl: './add-watermark.component.css',
  standalone: true
})
export class AddWatermarkComponent extends BasePdfToolComponent {
  toolId = 'add-watermark';

  watermarkText: string = '';
  watermarkPosition: string = 'center';

  positions = [
    { value: 'top-left',              label: 'Top Left' },
    { value: 'top-center',            label: 'Top Center' },
    { value: 'top-right',             label: 'Top Right' },
    { value: 'middle-left',           label: 'Middle Left' },
    { value: 'center',                label: 'Center' },
    { value: 'middle-right',          label: 'Middle Right' },
    { value: 'bottom-left',           label: 'Bottom Left' },
    { value: 'bottom-center',         label: 'Bottom Center' },
    { value: 'bottom-right',          label: 'Bottom Right' },
    { value: 'top-left-diagonal',     label: 'Top Left (Diagonal)' },
    { value: 'top-center-diagonal',   label: 'Top Center (Diagonal)' },
    { value: 'top-right-diagonal',    label: 'Top Right (Diagonal)' },
    { value: 'middle-left-diagonal',  label: 'Middle Left (Diagonal)' },
    { value: 'center-diagonal',       label: 'Center (Diagonal)' },
    { value: 'middle-right-diagonal', label: 'Middle Right (Diagonal)' },
    { value: 'bottom-left-diagonal',  label: 'Bottom Left (Diagonal)' },
    { value: 'bottom-center-diagonal',label: 'Bottom Center (Diagonal)' },
    { value: 'bottom-right-diagonal', label: 'Bottom Right (Diagonal)' },
  ];

  override convert(): void {
    if (!this.selectedFile && !this.fileKey) {
      this.toastService.show('Please select a file first', 'error');
      return;
    }
    if (!this.watermarkText.trim()) {
      this.toastService.show('Please enter watermark text', 'error');
      return;
    }

    this.isConverting = true;
    this.conversionResult = null;
    this.uploadProgress = 0;
    this.conversionStatus = 'Uploading...';
    this.startProgressSimulation(0, 85);

    const extraParams: { [key: string]: string } = {
      watermark_text: this.watermarkText,
      position: this.watermarkPosition,
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
                this.toastService.show('Watermark applied successfully', 'success');
                if (response.download_url) {
                  this.conversionResult = {
                    downloadUrl: response.download_url,
                    fileName: response.output_filename || 'watermarked_document.pdf'
                  };
                } else {
                  this.toastService.show('Conversion failed: No download URL returned', 'error');
                }
              } else {
                this.toastService.show('Failed to apply watermark', 'error');
              }
              break;
          }
        },
        error: (error) => {
          this.stopProgressSimulation(0);
          this.isConverting = false;
          this.uploadProgress = 0;
          this.conversionStatus = '';
          console.error('Watermark error:', error);
          const detail = error?.error?.detail;
          const msg = detail?.message || error?.error?.message || error?.message || 'An error occurred';
          this.toastService.show(msg, 'error');
        }
      });
  }

  override reset(): void {
    super.reset();
    this.watermarkText = '';
    this.watermarkPosition = 'center';
  }

  onFileChange(event: any): void {
    const file = event.target?.files?.[0];
    if (file) {
      this.onFileSelected(file);
    }
    event.target.value = '';
  }

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
