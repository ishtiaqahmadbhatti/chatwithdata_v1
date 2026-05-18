import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-word-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './word-to-pdf.component.html',
  styleUrl: './word-to-pdf.component.css',
  standalone: true
})
export class WordToPdfComponent extends BasePdfToolComponent {
  toolId = 'word-to-pdf';
}
