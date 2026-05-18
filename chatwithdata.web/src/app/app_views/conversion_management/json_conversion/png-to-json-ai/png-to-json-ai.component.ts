import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseJsonToolComponent } from '../base-json-tool.component';

@Component({
  selector: 'app-png-to-json-ai',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './png-to-json-ai.component.html',
  styleUrl: './png-to-json-ai.component.css',
  standalone: true
})
export class PngToJsonAiComponent extends BaseJsonToolComponent {
  toolId = 'png-to-json-ai';
}
