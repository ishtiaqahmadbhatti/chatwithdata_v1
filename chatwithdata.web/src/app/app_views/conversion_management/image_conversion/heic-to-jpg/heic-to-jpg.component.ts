import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-heic-to-jpg',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './heic-to-jpg.component.html',
  styleUrl: './heic-to-jpg.component.css',
  standalone: true
})
export class HeicToJpgComponent extends BaseImageToolComponent {
  toolId = 'heic-to-jpg';
}
