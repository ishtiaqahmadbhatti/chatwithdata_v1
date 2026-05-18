import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-avif-to-png',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './avif-to-png.component.html',
  styleUrl: './avif-to-png.component.css',
  standalone: true
})
export class AvifToPngComponent extends BaseImageToolComponent {
  toolId = 'avif-to-png';
}
