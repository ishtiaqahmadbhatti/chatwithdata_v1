import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseJsonToolComponent } from '../base-json-tool.component';

@Component({
  selector: 'app-json-validator',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './json-validator.component.html',
  styleUrl: './json-validator.component.css',
  standalone: true
})
export class JsonValidatorComponent extends BaseJsonToolComponent {
  toolId = 'json-validator';
  
  // Validation state
  useTextInput: boolean = false;
  jsonText: string = '';
  validationResult: any = null;
  isValid: boolean = false;
  statusMessage: string = '';

  setMode(useText: boolean) {
    this.useTextInput = useText;
    this.reset();
  }

  override onFileSelected(file: File): void {
    super.onFileSelected(file);
    this.validationResult = null;
    this.statusMessage = `File selected: ${file.name}`;
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
    this.uploadProgress = 0;
    this.validationResult = null;
    this.statusMessage = 'Validating JSON...';

    // Simulate progress for better UX
    const progressInterval = setInterval(() => {
      if (this.uploadProgress < 90) {
        this.uploadProgress += Math.random() * 30;
        if (this.uploadProgress > 90) this.uploadProgress = 90;
      }
    }, 100);

    const onComplete = (result: any) => {
      clearInterval(progressInterval);
      this.uploadProgress = 100;
      setTimeout(() => {
        this.handleValidationResult(result);
      }, 300);
    };

    const onError = (err: any) => {
      clearInterval(progressInterval);
      this.handleError(err);
    };

    if (this.useTextInput) {
      this.jsonService.validateJsonText(this.jsonText).subscribe({
        next: onComplete,
        error: onError
      });
    } else {
      this.jsonService.validateJsonFile(this.selectedFile!).subscribe({
        next: onComplete,
        error: onError
      });
    }
  }

  handleValidationResult(result: any) {
    this.isConverting = false;
    this.validationResult = result;
    this.isValid = result.valid === true;
    this.statusMessage = this.isValid ? '✅ JSON is valid!' : '❌ JSON is invalid!';
    
    if (this.isValid) {
      this.toastService.show('JSON is valid!', 'success');
    } else {
      this.toastService.show('JSON is invalid!', 'error');
    }
  }

  override handleError(error: any): void {
    super.handleError(error);
    this.statusMessage = 'Validation failed. Please try again.';
  }

  override reset(): void {
    super.reset();
    this.jsonText = '';
    this.validationResult = null;
    this.isValid = false;
    this.statusMessage = '';
  }

  parseErrorText(result: any): string {
    if (!result) return '';
    if (typeof result === 'string') return result;
    return result.message || 'Unknown error';
  }

  copyToClipboard() {
    if (this.validationResult) {
      const text = this.parseErrorText(this.validationResult);
      navigator.clipboard.writeText(text).then(() => {
        this.toastService.show('Error details copied!', 'success');
      });
    }
  }
}
