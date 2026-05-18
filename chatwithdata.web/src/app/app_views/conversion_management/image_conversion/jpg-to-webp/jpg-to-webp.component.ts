import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-jpg-to-webp',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './jpg-to-webp.component.html',
  styleUrl: './jpg-to-webp.component.css',
  standalone: true
})
export class JpgToWebpComponent extends BaseImageToolComponent {
  toolId = 'jpg-to-webp';
}
