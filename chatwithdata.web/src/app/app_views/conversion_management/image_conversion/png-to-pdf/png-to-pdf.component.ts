import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-png-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './png-to-pdf.component.html',
  styleUrl: './png-to-pdf.component.css',
  standalone: true
})
export class PngToPdfComponent extends BaseImageToolComponent {
  toolId = 'png-to-pdf';
}
