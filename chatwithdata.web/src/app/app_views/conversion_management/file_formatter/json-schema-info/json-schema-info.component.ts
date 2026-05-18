import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseFileFormatterToolComponent } from '../base-file-formatter-tool.component';

@Component({
  selector: 'app-json-schema-info',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './json-schema-info.component.html',
  styleUrl: './json-schema-info.component.css',
  standalone: true
})
export class JsonSchemaInfoComponent extends BaseFileFormatterToolComponent {
  toolId = 'json-schema-info';

  // State
  useTextInput: boolean = false;
  jsonText: string = '';
  schemaInfo: any = null;
  statusMessage: string = '';

  setMode(useText: boolean) {
    this.useTextInput = useText;
    this.reset();
  }

  override onFileSelected(file: File): void {
    super.onFileSelected(file);
    this.schemaInfo = null;
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
    this.schemaInfo = null;
    this.statusMessage = 'Analyzing JSON structure...';

    const onComplete = (event: any) => {
        if (event.type === 4) { // Response
            this.isConverting = false;
            this.uploadProgress = 100;
            const response = event.body;
            if (response && response.success) {
                this.schemaInfo = response.details?.schema_info;
                this.statusMessage = '✅ Analysis complete!';
                this.toastService.show('JSON analyzed!', 'success');
            } else {
                this.statusMessage = '❌ Analysis failed.';
                this.toastService.show('Analysis failed.', 'error');
            }
        }
    };

    if (this.useTextInput) {
      const blob = new Blob([this.jsonText], { type: 'application/json' });
      const file = new File([blob], 'input.json', { type: 'application/json' });
      
      this.formatterService.ConvertFile(this.toolId, file).subscribe({
        next: onComplete,
        error: (err: any) => this.handleError(err)
      });
    } else {
      this.formatterService.ConvertFile(this.toolId, this.selectedFile).subscribe({
        next: onComplete,
        error: (err: any) => this.handleError(err)
      });
    }
  }

  override reset(): void {
    super.reset();
    this.jsonText = '';
    this.schemaInfo = null;
    this.statusMessage = '';
  }

  // Helper to format keys/structure for display
  getStructureKeys(properties: any): string[] {
    return properties ? Object.keys(properties) : [];
  }
}
