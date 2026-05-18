import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseFileFormatterToolComponent } from '../base-file-formatter-tool.component';

@Component({
  selector: 'app-format-xml',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './format-xml.component.html',
  styleUrl: './format-xml.component.css',
  standalone: true
})
export class FormatXmlComponent extends BaseFileFormatterToolComponent {
  toolId = 'format-xml';

  // Formatter state
  useTextInput: boolean = false;
  xmlText: string = '';
  indentSize: number = 2;
  formattedXmlPreview: string | null = null;
  statusMessage: string = '';

  setMode(useText: boolean) {
    this.useTextInput = useText;
    this.reset();
    if (useText) {
      this.outputFilename = 'formatted_xml';
    }
  }

  override onFileSelected(file: File): void {
    super.onFileSelected(file);
    this.formattedXmlPreview = null;
    this.statusMessage = `File selected: ${file.name}`;
    const baseName = file.name.substring(0, file.name.lastIndexOf('.')) || file.name;
    this.outputFilename = `${baseName}_formatted`;
  }

  override convert(): void {
    if (!this.useTextInput && !this.selectedFile) {
      this.toastService.show('Please select an XML file first.', 'warning');
      return;
    }

    if (this.useTextInput && !this.xmlText.trim()) {
      this.toastService.show('Please enter XML content.', 'warning');
      return;
    }

    this.isConverting = true;
    this.conversionResult = null;
    this.formattedXmlPreview = null;
    this.statusMessage = 'Formatting XML...';

    const params = { indent: this.indentSize.toString() };

    const onComplete = (event: any) => {
        if (event.type === 4) { // Response
           this.isConverting = false;
           this.uploadProgress = 100;
           const response = event.body;
           if (response && response.success) {
              this.formattedXmlPreview = response.details?.formatted_xml || null;
              this.statusMessage = '✅ XML formatted successfully!';
              if (response.download_url) {
                this.conversionResult = {
                  downloadUrl: response.download_url,
                  fileName: response.output_filename || 'formatted.xml'
                };
              }
           } else {
              this.statusMessage = '❌ Formatting failed.';
              this.toastService.show('Formatting failed.', 'error');
           }
        }
    };

    if (this.useTextInput) {
      this.uploadProgress = 0;
      const blob = new Blob([this.xmlText], { type: 'application/xml' });
      const file = new File([blob], 'input.xml', { type: 'application/xml' });

      this.formatterService.ConvertFile(this.toolId, file, this.outputFilename, '', params)
        .subscribe({
          next: onComplete,
          error: (err: any) => this.handleError(err)
        });
    } else {
      this.formatterService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, '', params)
        .subscribe({
          next: onComplete,
          error: (err: any) => this.handleError(err)
        });
    }
  }

  override reset(): void {
    super.reset();
    this.xmlText = '';
    this.formattedXmlPreview = null;
    this.outputFilename = '';
    this.statusMessage = '';
  }

  copyToClipboard() {
    if (this.formattedXmlPreview) {
      navigator.clipboard.writeText(this.formattedXmlPreview).then(() => {
        this.toastService.show('Formatted XML copied!', 'success');
      });
    }
  }
}
