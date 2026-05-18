import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseJsonToolComponent } from '../base-json-tool.component';

@Component({
  selector: 'app-yaml-to-json',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './yaml-to-json.component.html',
  styleUrl: './yaml-to-json.component.css',
  standalone: true
})
export class YamlToJsonComponent extends BaseJsonToolComponent {
  toolId = 'yaml-to-json';
}
