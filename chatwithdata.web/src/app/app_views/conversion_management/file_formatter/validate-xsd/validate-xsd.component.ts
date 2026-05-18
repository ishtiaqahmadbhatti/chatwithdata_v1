import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseFileFormatterToolComponent } from '../base-file-formatter-tool.component';

@Component({
  selector: 'app-validate-xsd',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './validate-xsd.component.html',
  styleUrl: './validate-xsd.component.css',
  standalone: true
})
export class ValidateXsdComponent extends BaseFileFormatterToolComponent {
  toolId = 'validate-xsd';

  // Validation state
  useTextInput: boolean = false;
  xsdText: string = '';
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
      this.toastService.show('Please select an XSD file first.', 'warning');
      return;
    }

    if (this.useTextInput && !this.xsdText.trim()) {
      this.toastService.show('Please enter XSD content.', 'warning');
      return;
    }

    this.isConverting = true;
    this.uploadProgress = 0;
    this.validationResult = null;
    this.statusMessage = 'Validating XSD...';

    const onComplete = (event: any) => {
        if (event.type === 4) { // Response
            this.uploadProgress = 100;
            setTimeout(() => {
                const result = event.body?.validation_result;
                this.handleValidationResult(result);
            }, 300);
        }
    };

    const onError = (err: any) => {
      this.handleError(err);
    };

    if (this.useTextInput) {
      const blob = new Blob([this.xsdText], { type: 'application/xml' }); // XSD is XML
      const file = new File([blob], 'schema.xsd', { type: 'application/xml' });
      
      this.formatterService.ConvertFile(this.toolId, file).subscribe({
        next: onComplete,
        error: onError
      });
    } else {
      this.formatterService.ConvertFile(this.toolId, this.selectedFile).subscribe({
        next: onComplete,
        error: onError
      });
    }
  }

  handleValidationResult(result: any) {
    this.isConverting = false;
    this.validationResult = result;
    this.isValid = result?.valid === true;
    this.statusMessage = this.isValid ? '✅ XSD is valid!' : '❌ XSD is invalid!';
    
    if (this.isValid) {
      this.toastService.show('XSD is valid!', 'success');
    } else {
      this.toastService.show('XSD is invalid!', 'error');
    }
  }

  override handleError(error: any): void {
    super.handleError(error);
    this.statusMessage = 'Validation failed. Please try again.';
  }

  override reset(): void {
    super.reset();
    this.xsdText = '';
    this.validationResult = null;
    this.isValid = false;
    this.statusMessage = '';
  }

  parseErrorText(result: any): string {
    if (!result) return '';
    if (result.errors && result.errors.length > 0) {
        return result.errors.join('\n');
    }
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
