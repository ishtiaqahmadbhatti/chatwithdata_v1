import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BasePdfToolComponent } from '../base-pdf-tool.component';
import { HttpEvent, HttpEventType } from '@angular/common/http';

@Component({
  selector: 'app-repair',
  imports: [CommonModule, FormsModule],
  templateUrl: './repair.component.html',
  styleUrl: './repair.component.css',
  standalone: true
})
export class RepairComponent extends BasePdfToolComponent {
  toolId = 'repair';

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

    this.pdfService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, this.fileKey)
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
                this.toastService.show('PDF repaired successfully', 'success');
                if (response.download_url) {
                  this.conversionResult = {
                    downloadUrl: response.download_url,
                    fileName: response.output_filename || 'repaired_document.pdf'
                  };
                  this.conversionStatus = 'Repair Completed! ✅';
                } else {
                  this.toastService.show('Conversion failed: No download URL returned', 'error');
                }
              } else {
                this.toastService.show('Failed to repair PDF', 'error');
              }
              break;
          }
        },
        error: (error) => {
          this.stopProgressSimulation(0);
          this.isConverting = false;
          this.uploadProgress = 0;
          this.conversionStatus = '';
          console.error('Repair error:', error);
          const detail = error?.error?.detail;
          const msg = detail?.message || error?.error?.message || error?.message || 'An error occurred';
          this.toastService.show(msg, 'error');
        }
      });
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
