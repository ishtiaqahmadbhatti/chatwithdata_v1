import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BasePdfToolComponent } from '../base-pdf-tool.component';
import { HttpEvent, HttpEventType } from '@angular/common/http';

@Component({
  selector: 'app-split',
  imports: [CommonModule, FormsModule],
  templateUrl: './split.component.html',
  styleUrl: './split.component.css',
  standalone: true
})
export class SplitComponent extends BasePdfToolComponent {
  toolId = 'split';

  // Split-specific state
  splitType: string = 'every_page';
  pageRanges: string = '';

  override convert(): void {
    if (!this.selectedFile && !this.fileKey) {
        this.toastService.show('Please select a file first', 'error');
        return;
    }

    if (this.splitType === 'page_ranges' && !this.pageRanges.trim()) {
        this.toastService.show('Please specify the page ranges', 'error');
        return;
    }

    this.isConverting = true;
    this.conversionResult = null;
    this.uploadProgress = 0;
    this.conversionStatus = 'Initializing...';

    const extraParams = {
        split_type: this.splitType,
        page_ranges: this.pageRanges,
        zip: 'true',
        output_prefix: this.outputFilename
    };

    this.pdfService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, this.fileKey, extraParams)
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
                        this.conversionStatus = 'Splitting PDF...';
                        setTimeout(() => {
                            const response = event.body;
                            if (response && response.download_url) {
                                this.conversionResult = {
                                    downloadUrl: response.download_url,
                                    fileName: response.output_filename || 'split_result.zip'
                                };
                                this.isConverting = false;
                                this.toastService.show('PDF split successfully! Ready to download.', 'success');
                            } else {
                                this.toastService.show('Conversion failed: No download URL returned.', 'error');
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

  override reset(): void {
      super.reset();
      this.splitType = 'every_page';
      this.pageRanges = '';
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
}
