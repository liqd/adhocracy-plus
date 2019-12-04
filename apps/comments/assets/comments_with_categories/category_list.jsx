import React from 'react'
import django from 'django'

const CategoryList = (props) => (
  <fieldset>
    <legend className="sr-only">{django.gettext('Choose categories for your comment')}</legend>
    {Object.keys(props.categoryChoices).map(objectKey => {
      var categoryCheck = props.categoryChoices[objectKey]
      var inputId = props.idPrefix + '_' + objectKey
      return (
        <div className="comment-category" key={objectKey}>
          <label className="comment-category_row" htmlFor={inputId}>
            <input
              className="comment-category_input"
              type="checkbox"
              checked={props.categoriesChecked.indexOf(objectKey) > -1}
              onChange={props.handleControlFunc}
              id={inputId}
              value={categoryCheck}
            />
            <span className="badge comment-category_text"> {categoryCheck}</span>
          </label>
        </div>
      )
    })}
  </fieldset>
)

export default CategoryList
