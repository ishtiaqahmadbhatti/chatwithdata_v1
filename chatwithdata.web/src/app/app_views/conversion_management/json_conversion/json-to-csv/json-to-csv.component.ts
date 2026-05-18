import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseJsonToolComponent } from '../base-json-tool.component';

@Component({
  selector: 'app-json-to-csv',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './json-to-csv.component.html',
  styleUrl: './json-to-csv.component.css',
  standalone: true
})
export class JsonToCsvComponent extends BaseJsonToolComponent {
  toolId = 'json-to-csv';
  delimiter: string = ',';

  override onFileSelected(file: File): void {
    if (file && file.name.endsWith('.json')) {
      super.onFileSelected(file);
      this.toastService.show('JSON file selected successfully', 'success');
    } else {
      this.toastService.show('Please select a valid JSON file', 'error');
      this.selectedFile = null;
    }
  }

  override convert(): void {
    if (!this.selectedFile && !this.fileKey) {
      this.toastService.show('Please select a file first', 'error');
      return;
    }

    this.isConverting = true;
    this.conversionResult = null;
    this.uploadProgress = 0;
    this.conversionStatus = 'Initializing...';

    // Call service with extra delimiter parameter
    this.jsonService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, this.fileKey, { delimiter: this.delimiter })
      .subscribe({
        next: (event) => this.handleConversionEvent(event),
        error: (error) => this.handleError(error)
      });
  }

  override reset(): void {
    super.reset();
    this.delimiter = ',';
  }
}
