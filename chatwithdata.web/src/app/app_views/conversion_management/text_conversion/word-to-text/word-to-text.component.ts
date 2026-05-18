import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseTextToolComponent } from '../base-text-tool.component';

@Component({
  selector: 'app-word-to-text',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './word-to-text.component.html',
  styleUrl: './word-to-text.component.css',
  standalone: true
})
export class WordToTextComponent extends BaseTextToolComponent {
  toolId = 'word-to-text';
}
