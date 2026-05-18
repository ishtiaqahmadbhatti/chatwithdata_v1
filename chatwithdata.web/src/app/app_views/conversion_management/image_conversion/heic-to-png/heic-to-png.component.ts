import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-heic-to-png',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './heic-to-png.component.html',
  styleUrl: './heic-to-png.component.css',
  standalone: true
})
export class HeicToPngComponent extends BaseImageToolComponent {
  toolId = 'heic-to-png';
}
