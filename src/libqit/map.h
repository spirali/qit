#ifndef QIT_TAKE_H

#include <stdlib.h>

namespace qit {

template<typename Tin, typename Tout, typename F> class MapIterator {
	public:
		typedef Tout value_type;
		MapIterator() {}
		MapIterator(const Tin &iterator, const F &functor) : iterator(iterator), functor(functor) {}

		bool next(value_type &out) {
			typename Tin::value_type v;
			if (!iterator.next(v)) {
				return false;
			}
			out = functor(v);
			return true;
		}

		void reset() {
			iterator.reset();
		}

		QIT_ITERATOR_WRITE_METHOD

	protected:
		Tin iterator;
		int count;
		F functor;
};

}

#endif // QIT_TAKE_H
