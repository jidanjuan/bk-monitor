/*
 * Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
 *
 * License for BK-LOG 蓝鲸日志平台:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

import { Component, Emit, Prop } from 'vue-property-decorator';
import { Component as tsc } from 'vue-tsx-support';
import DatePicker from '@blueking/date-picker/vue2';
import { updateTimezone } from '../../language/dayjs';
import { DEFAULT_TIME_RANGE } from './utils';
import '@blueking/date-picker/vue2/vue2.css';

export type TimeRangeType = [string, string];

type TimeRangeDisplayType = 'normal' | 'simplicity';
interface IProps {
  value: TimeRangeType;
  type?: TimeRangeDisplayType;
  timezone?: string;
  needTimezone?: boolean;
}
interface IEvents {
  onChange: TimeRangeType;
  onTimezoneChange: string;
}

@Component
export default class TimeRange extends tsc<IProps, IEvents> {
  @Prop({ default: () => DEFAULT_TIME_RANGE, type: Array }) value: TimeRangeType; // 组件回显值
  @Prop({ default: 'simplicity', type: String }) type: TimeRangeDisplayType; // 组件回显值
  @Prop({ default: window.timezone, type: String }) timezone: TimeRangeDisplayType; // 组件回显值
  @Prop({ default: true, type: Boolean }) needTimezone: boolean; // 是否显示时区选择
  @Emit('change')
  handleModelValueChange(v: TimeRangeType) {
    this.$store.commit('retrieve/updateCachePickerValue', this.value);
    return v;
  }
  @Emit('timezoneChange')
  handleTimezoneChange(timezone: string) {
    timezone && updateTimezone(timezone);
    return timezone;
  }
  mounted() {
    this.$store.commit('retrieve/updateCachePickerValue', this.value);
  }
  render() {
    return (
      <div style='display: inline-flex'>
        <DatePicker
          ref='datePicker'
          modelValue={this.value}
          timezone={this.timezone}
          needTimezone={this.needTimezone}
          behavior={this.type}
          onChange={this.handleModelValueChange}
          onTimezoneChange={this.handleTimezoneChange}
        />
      </div>
    );
  }
}
