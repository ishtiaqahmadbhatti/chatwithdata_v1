import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-gif-to-webp',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './gif-to-webp.component.html',
  styleUrl: './gif-to-webp.component.css',
  standalone: true
})
export class GifToWebpComponent extends BaseImageToolComponent {
  toolId = 'gif-to-webp';
}
