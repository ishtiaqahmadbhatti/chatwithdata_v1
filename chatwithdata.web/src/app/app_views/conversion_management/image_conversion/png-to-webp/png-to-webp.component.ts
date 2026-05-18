import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-png-to-webp',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './png-to-webp.component.html',
  styleUrl: './png-to-webp.component.css',
  standalone: true
})
export class PngToWebpComponent extends BaseImageToolComponent {
  toolId = 'png-to-webp';
}
