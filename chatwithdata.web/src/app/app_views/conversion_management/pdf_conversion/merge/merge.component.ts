import { Component, inject, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { PDFConversionService } from '../../../../app_services/pdf_conversion.service';
import { ToastService } from '../../../../app_services/toast';

@Component({
  selector: 'app-merge',
  imports: [CommonModule, FormsModule],
  templateUrl: './merge.component.html',
  styleUrl: './merge.component.css',
  standalone: true
})
export class MergeComponent {
  // Services
  protected pdfService = inject(PDFConversionService);
  protected toastService = inject(ToastService);

  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  // Configuration
  toolId = 'merge';

  // State
  selectedFiles: File[] = [];
  outputFilename: string = '';
  suggestedFilename: string = '';
  isConverting: boolean = false;
  uploadProgress: number = 0;
  conversionStatus: string = 'Select at least 2 PDF files to begin.';
  conversionResult: { downloadUrl: string, fileName: string } | null = null;
  fileNameEdited: boolean = false;

  // Progress Simulation (Internal)
  private simulationInterval: any;

  triggerFileInput(): void {
    if (this.fileInput && this.fileInput.nativeElement) {
      this.fileInput.nativeElement.click();
    }
  }

  onFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const newFiles = Array.from(input.files);
      const existingPaths = new Set(this.selectedFiles.map(f => f.name));
      
      newFiles.forEach(file => {
        if (!existingPaths.has(file.name)) {
          this.selectedFiles.push(file);
        }
      });
      
      this.conversionResult = null;
      this.uploadProgress = 0;
      this.conversionStatus = `${this.selectedFiles.length} PDF files selected.`;
      
      this.updateSuggestedFileName();
    }
    if (input) {
      input.value = '';
    }
  }

  updateSuggestedFileName(): void {
    if (this.selectedFiles.length < 2) {
      this.suggestedFilename = '';
      if (!this.fileNameEdited) {
        this.outputFilename = '';
      }
      return;
    }

    const baseNames = this.selectedFiles
      .map(file => {
        const lastDot = file.name.lastIndexOf('.');
        return lastDot !== -1 ? file.name.substring(0, lastDot) : file.name;
      })
      .filter(name => name.length > 0);

    let suggestion = baseNames.slice(0, 4).join('_');
    if (baseNames.length > 4) {
      suggestion += `_plus${baseNames.length - 4}`;
    }

    suggestion = suggestion.replace(/[^A-Za-z0-9._-]/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '');
    if (!suggestion) {
      suggestion = 'merged_document';
    }

    this.suggestedFilename = suggestion;
    if (!this.fileNameEdited) {
      this.outputFilename = suggestion;
    }
  }

  onFilenameChange(): void {
    this.fileNameEdited = this.outputFilename.trim().length > 0;
  }

  moveFileUp(index: number): void {
    if (index > 0) {
      const file = this.selectedFiles[index];
      this.selectedFiles[index] = this.selectedFiles[index - 1];
      this.selectedFiles[index - 1] = file;
      this.updateSuggestedFileName();
    }
  }

  moveFileDown(index: number): void {
    if (index < this.selectedFiles.length - 1) {
      const file = this.selectedFiles[index];
      this.selectedFiles[index] = this.selectedFiles[index + 1];
      this.selectedFiles[index + 1] = file;
      this.updateSuggestedFileName();
    }
  }

  removeFile(index: number): void {
    this.selectedFiles.splice(index, 1);
    this.conversionResult = null;
    
    if (this.selectedFiles.length < 2) {
      this.conversionStatus = 'Select at least 2 PDF files to begin.';
    } else {
      this.conversionStatus = `${this.selectedFiles.length} PDF files selected.`;
    }
    this.updateSuggestedFileName();
  }

  getTotalSize(): string {
    const totalBytes = this.selectedFiles.reduce((acc, file) => acc + file.size, 0);
    return this.formatBytes(totalBytes);
  }

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Simulation helpers (matching base class logic)
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
    if (this.selectedFiles.length < 2) {
      this.toastService.show('Please select at least 2 PDF files before merging.', 'error');
      return;
    }

    this.isConverting = true;
    this.conversionResult = null;
    this.uploadProgress = 0;
    this.conversionStatus = 'Merging PDFs...';
    this.startProgressSimulation(0, 85);

    const finalFilename = this.outputFilename.trim() || this.suggestedFilename || 'merged_document';

    this.pdfService.ConvertMultipleFiles(this.toolId, this.selectedFiles, finalFilename)
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
                this.toastService.show('PDFs merged successfully', 'success');
                if (response.download_url) {
                  this.conversionResult = {
                    downloadUrl: response.download_url,
                    fileName: response.output_filename || 'merged_document.pdf'
                  };
                  this.conversionStatus = 'Merge Completed! ✅';
                } else {
                  this.toastService.show('Merge failed: No download URL returned', 'error');
                }
              } else {
                this.toastService.show('Failed to merge PDFs', 'error');
              }
              break;
          }
        },
        error: (error) => {
          this.stopProgressSimulation(0);
          this.isConverting = false;
          this.uploadProgress = 0;
          this.conversionStatus = '';
          console.error('Merge error:', error);
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
    this.selectedFiles = [];
    this.outputFilename = '';
    this.suggestedFilename = '';
    this.fileNameEdited = false;
    this.isConverting = false;
    this.conversionResult = null;
    this.conversionStatus = 'Select at least 2 PDF files to begin.';
    this.uploadProgress = 0;
    this.stopProgressSimulation();
  }
}
