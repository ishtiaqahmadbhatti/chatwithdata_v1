import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseTextToolComponent } from '../base-text-tool.component';

@Component({
  selector: 'app-srt-to-text',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './srt-to-text.component.html',
  styleUrl: './srt-to-text.component.css',
  standalone: true
})
export class SrtToTextComponent extends BaseTextToolComponent {
  toolId = 'srt-to-text';
}
