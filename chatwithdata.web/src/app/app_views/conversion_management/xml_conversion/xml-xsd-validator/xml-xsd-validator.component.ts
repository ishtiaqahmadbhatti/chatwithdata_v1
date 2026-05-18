import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseXmlToolComponent } from '../base-xml-tool.component';

@Component({
  selector: 'app-xml-xsd-validator',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './xml-xsd-validator.component.html',
  styleUrl: './xml-xsd-validator.component.css',
  standalone: true
})
export class XmlXsdValidatorComponent extends BaseXmlToolComponent {
  toolId = 'xml-xsd-validator';

  selectedXmlFile: File | null = null;
  selectedXsdFile: File | null = null;
  isValid: boolean = false;
  validationResultText: string | null = null;
  statusMessage: string = 'Select XML file (and optional XSD) to validate.';

  onXmlFileSelected(file: File): void {
    if (file) {
      this.selectedXmlFile = file;
      this.validationResultText = null;
      this.statusMessage = `XML selected: ${file.name}`;
      this.toastService.show('XML file selected', 'success');
    }
  }

  onXsdFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedXsdFile = file;
      this.validationResultText = null;
      this.toastService.show('XSD file selected', 'success');
    }
  }

  override convert(): void {
    if (!this.selectedXmlFile) {
      this.toastService.show('Please select an XML file first', 'error');
      return;
    }

    this.isConverting = true;
    this.validationResultText = null;
    this.uploadProgress = 0;
    this.statusMessage = 'Validating...';

    this.xmlService.ValidateXmlXsd(this.selectedXmlFile, this.selectedXsdFile)
      .subscribe({
        next: (event: HttpEvent<any>) => {
          switch (event.type) {
            case HttpEventType.Sent:
              this.statusMessage = 'Request sent...';
              break;
            case HttpEventType.UploadProgress:
              if (event.total) {
                this.uploadProgress = Math.round(100 * event.loaded / event.total);
              }
              this.statusMessage = `Uploading... ${this.uploadProgress}%`;
              break;
            case HttpEventType.Response:
              this.uploadProgress = 100;
              const response = event.body;
              if (response && response.success) {
                try {
                  const resultData = JSON.parse(response.converted_data);
                  this.isValid = resultData.valid;
                  this.validationResultText = JSON.stringify(resultData, null, 2);
                  this.statusMessage = this.isValid ? 'Validation Successful: XML is Valid' : 'Validation Failed: XML is Invalid';
                } catch (e) {
                  this.isValid = false;
                  this.validationResultText = response.converted_data;
                  this.statusMessage = 'Validation completed with issues';
                }
              } else {
                this.statusMessage = 'Validation failed';
              }
              this.isConverting = false;
              break;
          }
        },
        error: (error) => {
          this.isConverting = false;
          this.statusMessage = 'Validation error occurred';
          this.handleError(error);
        }
      });
  }

  override reset(): void {
    this.selectedXmlFile = null;
    this.selectedXsdFile = null;
    this.validationResultText = null;
    this.isConverting = false;
    this.statusMessage = 'Select XML file (and optional XSD) to validate.';
  }

  parseErrorText(jsonResult: string): string {
    try {
      const json = JSON.parse(jsonResult);
      if (json.errors && Array.isArray(json.errors)) {
        return json.errors.map((e: any) => `• ${e}`).join('\n');
      }
      if (json.message) {
        return json.message;
      }
      return jsonResult;
    } catch (e) {
      return jsonResult;
    }
  }

  copyToClipboard(): void {
    if (this.validationResultText) {
      navigator.clipboard.writeText(this.validationResultText);
      this.toastService.show('Result copied to clipboard', 'success');
    }
  }
}
