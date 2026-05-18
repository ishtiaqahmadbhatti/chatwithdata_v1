import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BasePdfToolComponent } from '../base-pdf-tool.component';
import { HttpEvent, HttpEventType } from '@angular/common/http';

@Component({
  selector: 'app-add-page-numbers',
  imports: [CommonModule, FormsModule],
  templateUrl: './add-page-numbers.component.html',
  styleUrl: './add-page-numbers.component.css',
  standalone: true
})
export class AddPageNumbersComponent extends BasePdfToolComponent {
  toolId = 'add-page-numbers';

  position: string = 'bottom-center';
  startPage: number = 1;
  format: string = '{page}';
  fontSize: number = 12;

  positions = [
    { value: 'top-left', label: 'Top Left' },
    { value: 'top-center', label: 'Top Center' },
    { value: 'top-right', label: 'Top Right' },
    { value: 'bottom-left', label: 'Bottom Left' },
    { value: 'bottom-center', label: 'Bottom Center' },
    { value: 'bottom-right', label: 'Bottom Right' },
  ];

  override convert(): void {
    if (!this.selectedFile && !this.fileKey) {
      this.toastService.show('Please select a file first', 'error');
      return;
    }

    this.isConverting = true;
    this.conversionResult = null;
    this.uploadProgress = 0;
    this.conversionStatus = 'Uploading...';
    this.startProgressSimulation(0, 85);

    const extraParams: { [key: string]: string } = {
      position: this.position,
      start_page: this.startPage.toString(),
      format: this.format,
      font_size: this.fontSize.toString(),
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
                this.toastService.show('Page numbers added successfully', 'success');
                if (response.download_url) {
                  this.conversionResult = {
                    downloadUrl: response.download_url,
                    fileName: response.output_filename || 'numbered_document.pdf'
                  };
                } else {
                  this.toastService.show('Conversion failed: No download URL returned', 'error');
                }
              } else {
                this.toastService.show('Failed to add page numbers', 'error');
              }
              break;
          }
        },
        error: (error) => {
          this.stopProgressSimulation(0);
          this.isConverting = false;
          this.uploadProgress = 0;
          this.conversionStatus = '';
          console.error('Add page numbers error:', error);
          const detail = error?.error?.detail;
          const msg = detail?.message || error?.error?.message || error?.message || 'An error occurred';
          this.toastService.show(msg, 'error');
        }
      });
  }

  override reset(): void {
    super.reset();
    this.position = 'bottom-center';
    this.startPage = 1;
    this.format = '{page}';
    this.fontSize = 12;
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
