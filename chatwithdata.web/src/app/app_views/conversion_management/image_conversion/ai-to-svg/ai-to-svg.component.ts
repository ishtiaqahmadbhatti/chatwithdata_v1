import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-ai-to-svg',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './ai-to-svg.component.html',
  styleUrl: './ai-to-svg.component.css',
  standalone: true
})
export class AiToSvgComponent extends BaseImageToolComponent {
  toolId = 'ai-to-svg';
}
