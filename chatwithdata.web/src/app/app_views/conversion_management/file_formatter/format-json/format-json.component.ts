import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseFileFormatterToolComponent } from '../base-file-formatter-tool.component';

@Component({
  selector: 'app-format-json',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './format-json.component.html',
  styleUrl: './format-json.component.css',
  standalone: true
})
export class FormatJsonComponent extends BaseFileFormatterToolComponent {
  toolId = 'format-json';

  // Formatter state
  useTextInput: boolean = false;
  jsonText: string = '';
  indentSize: number = 2;
  formattedJsonPreview: string | null = null;
  statusMessage: string = '';

  setMode(useText: boolean) {
    this.useTextInput = useText;
    this.reset();
    if (useText) {
      this.outputFilename = 'formatted_json';
    }
  }

  override onFileSelected(file: File): void {
    super.onFileSelected(file);
    this.formattedJsonPreview = null;
    this.statusMessage = `File selected: ${file.name}`;
    const baseName = file.name.substring(0, file.name.lastIndexOf('.')) || file.name;
    this.outputFilename = `${baseName}_formatted`;
  }

  override convert(): void {
    if (!this.useTextInput && !this.selectedFile) {
      this.toastService.show('Please select a JSON file first.', 'warning');
      return;
    }

    if (this.useTextInput && !this.jsonText.trim()) {
      this.toastService.show('Please enter JSON content.', 'warning');
      return;
    }

    this.isConverting = true;
    this.conversionResult = null;
    this.formattedJsonPreview = null;
    this.statusMessage = 'Formatting JSON...';

    const params = { indent: this.indentSize.toString() };

    if (this.useTextInput) {
      this.uploadProgress = 0;
      const blob = new Blob([this.jsonText], { type: 'application/json' });
      const file = new File([blob], 'input.json', { type: 'application/json' });

      this.formatterService.ConvertFile(this.toolId, file, this.outputFilename, '', params)
        .subscribe({
          next: (event: any) => {
            if (event.type === 1) { // Sent
               this.statusMessage = 'Uploading content...';
            } else if (event.type === 4) { // Response
               this.isConverting = false;
               this.uploadProgress = 100;
               const response = event.body;
               if (response && response.success) {
                  this.formattedJsonPreview = response.details?.formatted_json || null;
                  this.statusMessage = '✅ JSON formatted successfully!';
                  if (response.download_url) {
                    this.conversionResult = {
                      downloadUrl: response.download_url,
                      fileName: response.output_filename || 'formatted.json'
                    };
                  }
               } else {
                  this.statusMessage = '❌ Formatting failed.';
                  this.toastService.show('Formatting failed.', 'error');
               }
            }
          },
          error: (err) => {
            this.handleError(err);
          }
        });
    } else {
      // For file upload
      this.formatterService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, '', params)
        .subscribe({
          next: (event: any) => {
             if (event.type === 4) {
                this.isConverting = false;
                const response = event.body;
                if (response && response.success) {
                    this.formattedJsonPreview = response.details?.formatted_json || null;
                    this.statusMessage = '✅ Success!';
                    if (response.download_url) {
                        this.conversionResult = {
                          downloadUrl: response.download_url,
                          fileName: response.output_filename || 'formatted.json'
                        };
                    }
                }
             }
          },
          error: (err: any) => this.handleError(err)
        });
    }
  }

  override reset(): void {
    super.reset();
    this.jsonText = '';
    this.formattedJsonPreview = null;
    this.outputFilename = '';
    this.statusMessage = '';
  }

  copyToClipboard() {
    if (this.formattedJsonPreview) {
      navigator.clipboard.writeText(this.formattedJsonPreview).then(() => {
        this.toastService.show('Formatted JSON copied!', 'success');
      });
    }
  }
}
