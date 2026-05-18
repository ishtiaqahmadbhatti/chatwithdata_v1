import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseTextToolComponent } from '../base-text-tool.component';

@Component({
  selector: 'app-vtt-to-text',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './vtt-to-text.component.html',
  styleUrl: './vtt-to-text.component.css',
  standalone: true
})
export class VttToTextComponent extends BaseTextToolComponent {
  toolId = 'vtt-to-text';
}
