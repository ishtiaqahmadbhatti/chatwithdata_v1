import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseJsonToolComponent } from '../base-json-tool.component';

@Component({
  selector: 'app-json-formatter',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './json-formatter.component.html',
  styleUrl: './json-formatter.component.css',
  standalone: true
})
export class JsonFormatterComponent extends BaseJsonToolComponent {
  toolId = 'json-formatter';
  
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
    // Set suggested name based on selected file
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
      this.isConverting = true;
      this.uploadProgress = 0;
      this.statusMessage = 'Formatting JSON...';
      
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        if (this.uploadProgress < 90) {
          this.uploadProgress += Math.random() * 30;
          if (this.uploadProgress > 90) this.uploadProgress = 90;
        }
      }, 100);

      this.jsonService.formatJsonText(this.jsonText, this.indentSize, this.outputFilename).subscribe({
        next: (response: any) => {
          clearInterval(progressInterval);
          this.uploadProgress = 100;
          
          setTimeout(() => {
            this.isConverting = false;
            const isSuccess = response && (response.success === true || response.status === 'success');
            const data = response.converted_data || response.formatted_json || response.preview;
            
            if (isSuccess && data) {
              this.formattedJsonPreview = data;
              this.statusMessage = '✅ JSON formatted successfully!';
              this.toastService.show('JSON formatted!', 'success');
              
              if (response.download_url) {
                this.conversionResult = {
                  downloadUrl: response.download_url,
                  fileName: response.output_filename || 'formatted.json'
                };
              }
            } else {
              const errorMsg = response.message || 'Formatting failed or empty response.';
              this.statusMessage = `❌ ${errorMsg}`;
              this.toastService.show(errorMsg, 'error');
            }
          }, 300); // Small delay to show 100%
        },
        error: (err) => {
          clearInterval(progressInterval);
          this.handleError(err);
        }
      });
    } else {
      console.log('Converting JSON file:', this.selectedFile?.name);
      this.jsonService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, '', params).subscribe({
        next: (event: any) => {
          this.handleConversionEvent(event);
          if (event.type === 4 && event.body) {
             console.log('File Conversion Body:', event.body);
             const body = event.body;
             const data = body.converted_data || body.formatted_json || body.preview;
             if (data) {
                this.formattedJsonPreview = data;
             }
          }
        },
        error: (err) => {
          console.error('File Formatter Error:', err);
          this.handleError(err);
        }
      });
    }
  }

  override handleError(error: any): void {
    this.isConverting = false;
    let errorMessage = 'An error occurred during formatting.';
    
    if (error.error && error.error.message) {
      errorMessage = error.error.message;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    this.statusMessage = `❌ ${errorMessage}`;
    this.toastService.show(errorMessage, 'error');
  }

  override reset(): void {
    super.reset();
    this.jsonText = '';
    this.formattedJsonPreview = null;
    this.outputFilename = 'formatted_json';
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
