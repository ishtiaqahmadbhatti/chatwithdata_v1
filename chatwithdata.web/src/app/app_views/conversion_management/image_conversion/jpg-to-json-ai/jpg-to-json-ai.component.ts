import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-jpg-to-json-ai',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './jpg-to-json-ai.component.html',
  styleUrl: './jpg-to-json-ai.component.css',
  standalone: true
})
export class JpgToJsonAiComponent extends BaseImageToolComponent {
  toolId = 'jpg-to-json-ai';
}
