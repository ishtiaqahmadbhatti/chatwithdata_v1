import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOcrToolComponent } from '../base-ocr-tool.component';

@Component({
  selector: 'app-jpg-to-text',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './jpg-to-text.component.html',
  styleUrl: './jpg-to-text.component.css',
  standalone: true
})
export class JpgToTextComponent extends BaseOcrToolComponent {
  toolId = 'jpg-to-text';
}
