import React from 'react'
import { classNames } from 'adhocracy4'

export default function FeedPagination ({ page, totalPages, onClickNext, onClickPrevious, onClickPage }) {
  const maxVisiblePages = 5
  let startPage = Math.max(1, page - Math.floor(maxVisiblePages / 2))
  const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1)

  if (endPage - startPage + 1 < maxVisiblePages) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1)
  }

  const pageNumbers = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i)

  return (
    <div className="feed-list__pagination">
      <button
        className="feed-list__pagination-item feed-list__pagination-button"
        disabled={page === 1}
        onClick={onClickPrevious}
      >
        <i className="fa-solid fa-angle-left feed-list__pagination-icon" />
      </button>

      {startPage > 1 && (
        <>
          <button className="feed-list__pagination-item feed-list__pagination-button" onClick={() => onClickPage(1)}>1</button>
          {startPage > 2 && <span className="feed-list__pagination-item">...</span>}
        </>
      )}

      {pageNumbers.map((pageNum) => (
        <button
          key={pageNum}
          className={classNames(
            'feed-list__pagination-item feed-list__pagination-button',
            page === pageNum && 'feed-list__pagination-item--active'
          )}
          onClick={() => onClickPage(pageNum)}
        >
          {pageNum}
        </button>
      ))}

      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && <span className="feed-list__pagination-item">...</span>}
          <button className="feed-list__pagination-item feed-list__pagination-button" onClick={() => onClickPage(totalPages)}>{totalPages}</button>
        </>
      )}

      <button
        className="feed-list__pagination-item feed-list__pagination-button"
        disabled={page === totalPages}
        onClick={onClickNext}
      >
        <i className="fa-solid fa-angle-right feed-list__pagination-icon" />
      </button>
    </div>
  )
}
