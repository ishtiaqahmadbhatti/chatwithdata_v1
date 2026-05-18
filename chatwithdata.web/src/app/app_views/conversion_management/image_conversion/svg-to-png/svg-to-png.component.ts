import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-svg-to-png',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './svg-to-png.component.html',
  styleUrl: './svg-to-png.component.css',
  standalone: true
})
export class SvgToPngComponent extends BaseImageToolComponent {
  toolId = 'svg-to-png';
}
