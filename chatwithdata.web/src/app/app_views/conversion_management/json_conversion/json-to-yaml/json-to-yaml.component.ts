import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseJsonToolComponent } from '../base-json-tool.component';

@Component({
  selector: 'app-json-to-yaml',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './json-to-yaml.component.html',
  styleUrl: './json-to-yaml.component.css',
  standalone: true
})
export class JsonToYamlComponent extends BaseJsonToolComponent {
  toolId = 'json-to-yaml';
}
