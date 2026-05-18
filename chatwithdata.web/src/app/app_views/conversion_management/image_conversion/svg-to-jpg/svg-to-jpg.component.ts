import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-svg-to-jpg',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './svg-to-jpg.component.html',
  styleUrl: './svg-to-jpg.component.css',
  standalone: true
})
export class SvgToJpgComponent extends BaseImageToolComponent {
  toolId = 'svg-to-jpg';
}
