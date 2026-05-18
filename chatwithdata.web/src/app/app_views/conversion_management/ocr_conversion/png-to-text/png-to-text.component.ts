import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOcrToolComponent } from '../base-ocr-tool.component';

@Component({
  selector: 'app-png-to-text',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './png-to-text.component.html',
  styleUrl: './png-to-text.component.css',
  standalone: true
})
export class PngToTextComponent extends BaseOcrToolComponent {
  toolId = 'png-to-text';
}
