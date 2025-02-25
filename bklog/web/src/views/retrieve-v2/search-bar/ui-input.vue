<script setup>
  import { ref, computed, set } from 'vue';

  import { getOperatorKey, formatDateTimeField } from '@/common/util';
  import { operatorMapping, translateKeys } from './const-values';
  import useLocale from '@/hooks/use-locale';
  import useStore from '@/hooks/use-store';

  import {
    getInputQueryDefaultItem,
    getInputQueryIpSelectItem,
    FulltextOperatorKey,
    FulltextOperator,
  } from './const.common';
  import UiInputOptions from './ui-input-option.vue';
  import useFocusInput from './use-focus-input';
  import IPSelector from './ip-selector';

  const props = defineProps({
    value: {
      type: Array,
      required: true,
      default: () => [],
    },
  });

  const emit = defineEmits(['input', 'change', 'height-change']);
  const store = useStore();
  const { $t } = useLocale();

  const bkBizId = computed(() => store.state.bkBizId);

  /**
   * 格式化搜索标签渲染格式
   * @param {*} item
   */
  const formatModelValueItem = item => {
    if (typeof item?.value === 'string') {
      item.value = item.value.split(',');
    }

    if (!item?.relation) item.relation = 'OR';
    return { disabled: false, ...(item ?? {}) };
  };

  const handleHeightChange = height => {
    emit('height-change', height);
  };

  const operatorDictionary = computed(() => {
    const defVal = {
      [getOperatorKey(FulltextOperatorKey)]: { label: $t('包含'), operator: FulltextOperator },
    };
    return {
      ...defVal,
      ...store.state.operatorDictionary,
    };
  });

  /**
   * 获取操作符展示文本
   * @param {*} item
   */
  const getOperatorLabel = item => {
    if (item.field === '_ip-select_') {
      return '';
    }

    const key = item.field === '*' ? getOperatorKey(`*${item.operator}`) : getOperatorKey(item.operator);
    if (translateKeys.includes(operatorMapping[item.operator])) {
      return $t(operatorMapping[item.operator] ?? item.operator);
    }

    return (operatorMapping[item.operator] ?? operatorDictionary.value[key]?.label) ??  item.operator;
  };

  const refPopInstance = ref(null);
  const refUlRoot = ref(null);
  const refSearchInput = ref(null);
  const queryItem = ref('');
  const activeIndex = ref(null);
  const isInputFocus = ref(false);
  const showIpSelector = ref(false);

  const getSearchInputValue = () => {
    return refSearchInput.value?.value ?? '';
  };

  let inputValueLength = 0;

  const setSearchInputValue = val => {
    refSearchInput.value.value = val ?? '';
    inputValueLength = refSearchInput.value?.value?.length ?? 0;
  };

  const handleWrapperClickCapture = (e, { getTippyInstance }) => {
    const instance = getTippyInstance();
    const reference = instance?.reference;

    const target = refSearchInput.value?.closest('.search-item');
    if (reference) {
      // 如果当前是input focus激活的弹出提示
      // 判定当前是否为点击 ui 搜索框
      if (reference === target) {
        return e.target === refUlRoot.value;
      }

      // 判定当前点击是否为某一个条件选项
      return reference.contains(e.target);
    }

    return false;
  };

  // 是否为自动foucus到input
  // 自动focus不用弹出选择提示
  const isAutoFocus = ref(false);

  const {
    modelValue,
    isDocumentMousedown,
    setIsDocumentMousedown,
    getTippyInstance,
    handleInputBlur,
    isInstanceShown,
    delayShowInstance,
    repositionTippyInstance,
  } = useFocusInput(props, {
    onHeightChange: handleHeightChange,
    formatModelValueItem,
    refContent: refPopInstance,
    onShowFn: () => {
      setIsDocumentMousedown(true);
      refPopInstance.value?.beforeShowndFn?.();
    },
    onHiddenFn: () => {
      if (isDocumentMousedown.value) {
        setIsDocumentMousedown(false);
        return false;
      }

      refPopInstance.value?.afterHideFn?.();
      if (refSearchInput.value) {
        isAutoFocus.value = true;
        refSearchInput.value?.focus();
        setTimeout(() => {
          isAutoFocus.value = false;
        });
      }

      return true;
    },
    handleWrapperClick: handleWrapperClickCapture,
  });

  const debounceShowInstance = () => {
    const target = refSearchInput.value?.closest('.search-item');
    if (target) {
      delayShowInstance(target);
    }
  };

  const closeTippyInstance = () => {
    setIsDocumentMousedown(false);
    getTippyInstance()?.hide();
  };

  /**
   * 执行点击弹出操作项方法
   * @param {*} target 目标元素
   */
  const showTagListItems = target => {
    if (isInstanceShown()) {
      repositionTippyInstance();
      return;
    }

    delayShowInstance(target);
  };

  const getMatchName = field => {
    if (field === '*') return $t('全文');
    if (field === '_ip-select_') return $t('IP目标');
    return field;
  };

  const emitChange = value => {
    emit('input', value);
    emit('change', value);
  };

  const handleAddItem = e => {
    isInputFocus.value = false;
    const target = e.target.closest('.search-item');
    queryItem.value = '';
    activeIndex.value = null;
    showTagListItems(target);
  };

  const handleTagItemClick = (e, item, index) => {
    if (item.field === '_ip-select_') {
      showIpSelector.value = true;
      return;
    }

    queryItem.value = {};
    isInputFocus.value = false;
    if (!Array.isArray(item.value)) item.value = item.value.split(',');
    if (!item.relation) item.relation = 'OR';
    Object.assign(queryItem.value, item);
    const target = e.target.closest('.search-item');
    activeIndex.value = isInputFocus.value ? null : index;
    showTagListItems(target);
  };

  const handleDisabledTagItem = item => {
    set(item, 'disabled', !item.disabled);
    emitChange(modelValue.value);
  };

  const handleDeleteTagItem = (index, item) => {
    modelValue.value.splice(index, 1);
    emitChange(modelValue.value);
  };

  /**
   * 点击查询
   * @param payload
   */
  const handleSaveQueryClick = payload => {
    if (payload === 'ip-select-show') {
      const copyValue = getInputQueryIpSelectItem();
      if (!modelValue.value.some(f => f.field === copyValue.field)) {
        modelValue.value.push({ ...copyValue, disabled: false });
      }

      closeTippyInstance();
      setTimeout(() => {
        showIpSelector.value = true;
      }, 100);
      return;
    }

    const isPayloadValueEmpty = !(payload?.value?.length ?? 0);
    const isFulltextEnterVlaue = isInputFocus.value && isPayloadValueEmpty && !payload?.field;

    const inputVal = getSearchInputValue();
    // 如果是全文检索，未输入任何内容就点击回车
    // 此时提交无任何意义，禁止后续逻辑
    if (isFulltextEnterVlaue && !inputVal.length) {
      return;
    }

    let targetValue = formatModelValueItem(isFulltextEnterVlaue ? getInputQueryDefaultItem(inputVal) : payload);

    if (isInputFocus.value) {
      setSearchInputValue('');
    }

    if (activeIndex.value !== null && activeIndex.value >= 0) {
      Object.assign(modelValue.value[activeIndex.value], targetValue);
      emitChange(modelValue.value);
      closeTippyInstance();
      return;
    }

    modelValue.value.push({ ...targetValue, disabled: false });
    emitChange(modelValue.value);
    closeTippyInstance();
  };

  // 用于判定当前 key.enter 是全局绑定触发还是 input.key.enter触发
  const isGlobalKeyEnter = ref(false);
  const handleGlobalSaveQueryClick = payload => {
    isGlobalKeyEnter.value = true;
    handleSaveQueryClick(payload);
  };

  /**
   * input key enter
   * @param e
   */
  const handleInputValueEnter = () => {
    if (!isGlobalKeyEnter.value) {
      if (!(getTippyInstance().state.isShown ?? false)) {
        handleSaveQueryClick(undefined);
      }
    }

    isGlobalKeyEnter.value = false;
  };

  const handleCancelClick = () => {
    closeTippyInstance();
    setSearchInputValue('');
  };

  const handleFocusInput = () => {
    isInputFocus.value = true;
    activeIndex.value = null;
    queryItem.value = '';

    if (isAutoFocus.value) {
      return;
    }

    debounceShowInstance();
  };

  const handleFullTextInputBlur = e => {
    if (!isInstanceShown()) {
      handleInputBlur(e);
      inputValueLength = 0;
      queryItem.value = '';
    }
  };

  const handleInputValueChange = e => {
    if (inputValueLength === 0 && e.target.value.length > 0) {
      inputValueLength = e.target.value.length;
      debounceShowInstance();
    }

    queryItem.value = e.target.value;
  };

  // 键盘删除键
  const needDeleteItem = ref(false);
  const handleDeleteItem = e => {
    if (e.target.value) {
      needDeleteItem.value = false;
    }

    if (!e.target.value) {
      if (needDeleteItem.value) {
        if (modelValue.value.length >= 1) {
          modelValue.value.splice(-1, 1);
          emitChange(modelValue.value);
          closeTippyInstance();
        }
      }

      needDeleteItem.value = true;
    }
  };

  const handleIPChange = () => {
    emitChange(modelValue.value);
  };

  const renderItemText = (field, value) => {
    formatDateTimeField
  }
</script>

<template>
  <ul
    ref="refUlRoot"
    class="search-items"
  >
    <li
      class="search-item btn-add"
      @click.stop="handleAddItem"
    >
      <div class="tag-add">+</div>
      <div class="tag-text">{{ $t('添加条件') }}</div>
    </li>
    <li
      v-for="(item, index) in modelValue"
      :class="['search-item', 'tag-item', { disabled: item.disabled }]"
      :key="`${item.field}-${index}`"
      @click.stop="e => handleTagItemClick(e, item, index)"
    >
      <div class="tag-row match-name">
        {{ getMatchName(item.field) }}
        <span
          class="symbol"
          :data-operator="item.operator"
          >{{ getOperatorLabel(item) }}</span
        >
      </div>
      <div class="tag-row match-value">
        <template v-if="item.field === '_ip-select_'">
          <span class="match-value-text">
            <IPSelector
              v-model="item.value[0]"
              :isShow.sync="showIpSelector"
              :bkBizId="bkBizId"
              @change="handleIPChange"
            ></IPSelector>
          </span>
        </template>
        <template v-else-if="Array.isArray(item.value)">
          <span
            v-for="(child, childInex) in item.value"
            :key="childInex"
          >
            <span class="match-value-text">{{ formatDateTimeField(child, item.field_type) }}</span>
            <span
              v-if="childInex < item.value.length - 1"
              class="match-value-relation"
              >{{ item.relation }}</span
            >
          </span>
        </template>
        <template v-else>
          <span>{{ item.value }}</span>
        </template>
      </div>
      <div class="tag-options">
        <span
          :class="[
            'bklog-icon',
            { 'bklog-eye': !item.disabled, disabled: item.disabled, 'bklog-eye-slash': item.disabled },
          ]"
          @click.stop="e => handleDisabledTagItem(item, e)"
        ></span>
        <span
          class="bk-icon icon-close"
          @click.stop="() => handleDeleteTagItem(index, item)"
        ></span>
      </div>
    </li>
    <li class="search-item is-focus-input">
      <input
        ref="refSearchInput"
        class="tag-option-focus-input"
        type="text"
        @blur="handleFullTextInputBlur"
        @focus.stop="handleFocusInput"
        @input="handleInputValueChange"
        @keyup.delete="handleDeleteItem"
        @keyup.enter="handleInputValueEnter"
      />
    </li>
    <div style="display: none">
      <UiInputOptions
        ref="refPopInstance"
        :is-input-focus="isInputFocus"
        :value="queryItem"
        @cancel="handleCancelClick"
        @save="handleGlobalSaveQueryClick"
      ></UiInputOptions>
    </div>
  </ul>
</template>
<style scoped>
  @import './ui-input.scss';
  @import 'tippy.js/dist/tippy.css';
</style>
<style>
  .tippy-box {
    &[data-theme='log-light'] {
      color: #63656e;
      background-color: #fff;
      box-shadow: 0 2px 6px 0 #0000001a;

      .tippy-content {
        padding: 0;
      }

      .tippy-arrow {
        color: #fff;

        &::after {
          background-color: #fff;
          box-shadow: 0 2px 6px 0 #0000001a;
        }
      }
    }
  }
</style>
