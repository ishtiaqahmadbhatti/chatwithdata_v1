import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-webp-to-avif',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './webp-to-avif.component.html',
  styleUrl: './webp-to-avif.component.css',
  standalone: true
})
export class WebpToAvifComponent extends BaseImageToolComponent {
  toolId = 'webp-to-avif';
}
