import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BasePdfToolComponent } from '../base-pdf-tool.component';

@Component({
  selector: 'app-powerpoint-to-pdf',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './powerpoint-to-pdf.component.html',
  styleUrl: './powerpoint-to-pdf.component.css',
  standalone: true
})
export class PowerpointToPdfComponent extends BasePdfToolComponent {
  toolId = 'powerpoint-to-pdf';
}
