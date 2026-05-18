import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-metadata',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './metadata.component.html',
  styleUrl: './metadata.component.css',
  standalone: true
})
export class MetadataComponent extends BasePdfToolComponent {
  toolId = 'metadata';
  metadataResult: any = null;

  override convert(): void {
    if (!this.selectedFile && !this.fileKey) {
      this.toastService.show('Please select a file first', 'error');
      return;
    }

    this.isConverting = true;
    this.conversionResult = null;
    this.metadataResult = null;
    this.uploadProgress = 0;
    this.conversionStatus = 'Extracting Metadata...';
    this.startProgressSimulation(0, 95);

    this.pdfService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, this.fileKey)
      .subscribe({
        next: (event: any) => {
          if (event.type === 4) { // Response
            this.stopProgressSimulation(100);
            this.conversionStatus = 'Extracted! ✅';
            const response = event.body;
            if (response && response.success) {
              // Flatten metadata for easier display
              const rawMeta = response.metadata;
              this.metadataResult = {
                'Page Count': rawMeta.page_count,
                ...rawMeta.metadata
              };
              
              this.conversionResult = {
                downloadUrl: response.download_url,
                fileName: response.output_filename || 'metadata.json'
              };
              this.isConverting = false;
              this.toastService.show('Metadata extracted successfully', 'success');
            } else {
              this.handleError('Failed to extract metadata');
            }
          }
        },
        error: (err) => {
          this.stopProgressSimulation(0);
          this.handleError(err);
        }
      });
  }

  saveAsText(): void {
    if (!this.metadataResult) return;
    
    let textContent = `PDF Metadata Report\n`;
    textContent += `===================\n\n`;
    
    Object.keys(this.metadataResult).forEach(key => {
      const val = this.metadataResult[key];
      textContent += `${key}: ${val}\n`;
    });
    
    const blob = new Blob([textContent], { type: 'text/plain' });
    this.downloadBlob(blob, `${this.outputFilename || 'metadata'}_report.txt`);
    this.toastService.show('Metadata report saved as text', 'success');
  }

  override reset(): void {
    super.reset();
    this.metadataResult = null;
  }
}
