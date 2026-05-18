import { Component, inject, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { PDFConversionService } from '../../../../app_services/pdf_conversion.service';
import { ToastService } from '../../../../app_services/toast';

@Component({
  selector: 'app-compare',
  imports: [CommonModule, FormsModule],
  templateUrl: './compare.component.html',
  styleUrl: './compare.component.css',
  standalone: true
})
export class CompareComponent {
  // Services
  protected pdfService = inject(PDFConversionService);
  protected toastService = inject(ToastService);

  @ViewChild('fileInput1') fileInput1!: ElementRef<HTMLInputElement>;
  @ViewChild('fileInput2') fileInput2!: ElementRef<HTMLInputElement>;

  // Configuration
  toolId = 'compare';

  // State
  file1: File | null = null;
  file2: File | null = null;
  outputFilename: string = '';
  isConverting: boolean = false;
  uploadProgress: number = 0;
  conversionStatus: string = 'Select two PDF files to compare.';
  conversionResult: { downloadUrl: string, fileName: string } | null = null;

  // Progress Simulation (Internal)
  private simulationInterval: any;

  onFile1Selected(event: any): void {
    const file = event.target?.files?.[0];
    if (file) {
      this.file1 = file;
      this.conversionResult = null;
      this.uploadProgress = 0;
      this.updateStatus();
    }
    event.target.value = '';
  }

  onFile2Selected(event: any): void {
    const file = event.target?.files?.[0];
    if (file) {
      this.file2 = file;
      this.conversionResult = null;
      this.uploadProgress = 0;
      this.updateStatus();
    }
    event.target.value = '';
  }

  updateStatus(): void {
    if (!this.file1 && !this.file2) {
      this.conversionStatus = 'Select two PDF files to compare.';
    } else if (this.file1 && !this.file2) {
      this.conversionStatus = 'Select the second PDF file.';
    } else if (!this.file1 && this.file2) {
      this.conversionStatus = 'Select the first PDF file.';
    } else {
      this.conversionStatus = 'Ready to compare.';
    }
  }

  // Simulation helpers
  private startProgressSimulation(start: number, end: number): void {
    this.stopProgressSimulation();
    let current = start;
    this.simulationInterval = setInterval(() => {
      if (current < end) {
        const remaining = end - current;
        const increment = Math.max(0.1, remaining * 0.05);
        current += increment;
        this.uploadProgress = Math.round(current);
      } else {
        this.stopProgressSimulation();
      }
    }, 200);
  }

  private stopProgressSimulation(finalValue?: number): void {
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval);
      this.simulationInterval = null;
    }
    if (finalValue !== undefined) {
      this.uploadProgress = finalValue;
    }
  }

  convert(): void {
    if (!this.file1 || !this.file2) {
      this.toastService.show('Please select both PDF files to compare.', 'error');
      return;
    }

    this.isConverting = true;
    this.conversionResult = null;
    this.uploadProgress = 0;
    this.conversionStatus = 'Comparing PDFs...';
    this.startProgressSimulation(0, 85);

    this.pdfService.CompareFiles(this.toolId, this.file1, this.file2, this.outputFilename)
      .subscribe({
        next: (event: HttpEvent<any>) => {
          switch (event.type) {
            case HttpEventType.Sent:
              this.conversionStatus = 'Uploading files...';
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
              this.conversionStatus = `Uploading files... ${this.uploadProgress}%`;
              break;
            case HttpEventType.ResponseHeader:
              this.conversionStatus = 'Processing...';
              break;
            case HttpEventType.Response:
              this.stopProgressSimulation(100);
              this.isConverting = false;
              if (event.body && event.body.success) {
                const response = event.body;
                this.toastService.show('PDFs compared successfully', 'success');
                if (response.download_url) {
                  this.conversionResult = {
                    downloadUrl: response.download_url,
                    fileName: response.output_filename || 'comparison_report.pdf'
                  };
                  this.conversionStatus = 'Comparison Ready! ✅';
                } else {
                  this.toastService.show('Comparison failed: No download URL returned', 'error');
                }
              } else {
                this.toastService.show('Failed to compare PDFs', 'error');
              }
              break;
          }
        },
        error: (error) => {
          this.stopProgressSimulation(0);
          this.isConverting = false;
          this.uploadProgress = 0;
          this.conversionStatus = '';
          console.error('Compare error:', error);
          const detail = error?.error?.detail;
          const msg = detail?.message || error?.error?.message || error?.message || 'An error occurred';
          this.toastService.show(msg, 'error');
        }
      });
  }

  saveFile(): void {
    if (!this.conversionResult) return;
    this.pdfService.downloadFile(this.conversionResult.downloadUrl).subscribe({
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
    this.file1 = null;
    this.file2 = null;
    this.outputFilename = '';
    this.isConverting = false;
    this.conversionResult = null;
    this.conversionStatus = 'Select two PDF files to compare.';
    this.uploadProgress = 0;
    this.stopProgressSimulation();
  }

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
