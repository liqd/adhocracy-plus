import React from 'react'
import PropTypes from 'prop-types'
import django from 'django'

const CommentManageDropdown = (props) => {
  return (
    <ul className="nav navbar-nav comment-dropdown">
      <li className="dropdown">
        <button
          type="button" className="dropdown-toggle btn btn--sm btn--no-border" aria-haspopup="true"
          aria-expanded="false" data-toggle="dropdown"
        >
          <i className="icon-userbar" aria-hidden="true" />
        </button>
        <ul className="dropdown-menu dropdown-menu-right">
          {props.renderModeratorOptions && [
            <li key="1">
              <button className="dropdown-item btn btn--sm btn-link" type="button" onClick={props.handleToggleEdit}>{django.gettext('Edit')}</button>
            </li>,
            <li className="divider" key="2" />,
            <li key="3"><a className="dropdown-item btn btn--sm btn-link" href={`#comment_delete_${props.id}`} data-toggle="modal">{django.gettext('Delete')}</a></li>,
            <li className="divider" key="4" />
          ]}
        </ul>
      </li>
    </ul>
  )
}

CommentManageDropdown.propTypes = {
  handleToggleEdit: PropTypes.func,
  id: PropTypes.number,
  renderModeratorOptions: PropTypes.bool
}

export default CommentManageDropdown
