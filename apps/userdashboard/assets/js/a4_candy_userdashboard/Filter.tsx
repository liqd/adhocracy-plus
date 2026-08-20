import React, { useState } from 'react'
import django from 'django'
import type { FilterItem } from './types'

const getItemByValue = (items: FilterItem[], value: string) => {
  return items.find(item => item.value === value)
}

interface FilterProps {
  filterItems: FilterItem[]
  selectedFilter: string
  filterClass?: string
  filterText?: string
  onFilterChange: (value: string) => void
}

export const Filter = (props: FilterProps) => {
  const [currFilterItem, setCurrFilterItem] =
    useState<FilterItem | undefined>(getItemByValue(props.filterItems, props.selectedFilter))

  const onSelectFilter = (filterItem: FilterItem) => {
    setCurrFilterItem(filterItem)
    props.onFilterChange(filterItem.value)
  }

  return (
    <div className={props.filterClass}>
      <button
        type="button"
        className="dropdown-toggle btn btn--light btn--select"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        {props.filterText}: {currFilterItem?.label}
        <i className="fa fa-caret-down" aria-hidden="true" />
      </button>
      <ul className="dropdown-menu">
        {props.filterItems.map((filterItem, i) => (
          <li key={i + '_' + filterItem.label}>
            <button onClick={() => onSelectFilter(filterItem)}>
              {django.gettext(filterItem.label)}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
